import copy
import ldap
from ldap.controls import SimplePagedResultsControl
import ldapurl
import logging


import basegenerator
import errors
import factory
import rootDSE
import utils

__all__ = [ 'create_from_uri', 'LDAPReader']


class PagedResultsGenerator(object):
    def paged_search_ext_s(self,base,scope,filterstr='(objectClass=*)',attrlist=None,attrsonly=0,serverctrls=None,clientctrls=None,timeout=-1,sizelimit=0, page_size=1000):
        """
        Behaves exactly like LDAPObject.search_ext_s() but internally uses the
        simple paged results control to retrieve search results in chunks.
        
        Taken on 2013-07-10 from : 
        https://bitbucket.org/jaraco/python-ldap/src/f208b6338a28/Demo/paged_search_ext_s.py
        Converted to a generator
        
        Added range support based on :
        http://stackoverflow.com/a/1711862/591064

        """
        req_ctrl = SimplePagedResultsControl(True,size=page_size,cookie='')
      
        # Send first search request
        msgid = self.search_ext(
          base,
          scope,
          filterstr=filterstr,
          attrlist=attrlist,
          attrsonly=attrsonly,
          serverctrls=(serverctrls or [])+[req_ctrl],
          clientctrls=clientctrls,
          timeout=timeout,
          sizelimit=sizelimit
        )
        
        while True:
            rtype, rdata, rmsgid, rctrls = self.result3(msgid)

            #singleresult is a list of pyldap tuple in the form [(dn, dict),(dn,dict)]
            for singleresult in rdata:
                #Range support idea found on StackOverflow
                #http://stackoverflow.com/a/1711862/591064#
                dn = singleresult[0]
             
                for attrname in singleresult[1]:
                    if ';range=' in attrname:
                      #
                      # parse range attr
                      #
                      actual_attrname, range_stmt = attrname.split(';')
                      bound_lower, bound_upper = [
                        int(x) for x in range_stmt.split('=')[1].split('-')
                      ]
             
                      step = bound_upper - bound_lower + 1
                      while True:
                        attr_next = '%s;range=%d-%d' % (
                          actual_attrname, bound_lower, bound_upper
                        )
             
                        dn, attrs = self.search_s(
                          dn, ldap.SCOPE_BASE, attrlist = [attr_next])[0]
             
                        assert len(attrs) == 1
             
                        ret_attrname = attrs.keys()[0]
             
                        singleresult[1][actual_attrname].extend(attrs[ret_attrname])
                        if ret_attrname.endswith('-*'):
                          break
             
                        bound_lower = bound_upper + 1
                        bound_upper += step

                yield singleresult
          
            # Extract the simple paged results response control
            pctrls = [
                c
                for c in rctrls
                if c.controlType == SimplePagedResultsControl.controlType
            ]
            if pctrls:
                if pctrls[0].cookie:
                    # Copy cookie from response control to request control
                    req_ctrl.cookie = pctrls[0].cookie
                    msgid = self.search_ext(
                        base,
                        scope,
                        filterstr=filterstr,
                        attrlist=attrlist,
                        attrsonly=attrsonly,
                        serverctrls=(serverctrls or [])+[req_ctrl],
                        clientctrls=clientctrls,
                        timeout=timeout,
                        sizelimit=sizelimit
                    )
                else:
                    break

class LDAPObjectStream(ldap.ldapobject.LDAPObject, PagedResultsGenerator):
    pass

        
class LDAPReader(basegenerator.BaseGenerator):
    def __init__(self, uri, serverctrls=None):
        #FIXME : try and handle ValueError ?
        self.ldap_url = ldapurl.LDAPUrl(uri)

        #Will be use to understand queries with mongolito metadata later
        self.base = self.ldap_url.dn
        self.serverctrls = serverctrls

        self.connection = LDAPObjectStream(self.ldap_url.unparse())

        self.connection.set_option(ldap.OPT_REFERRALS, 0)
        self.connection.set_option(ldap.OPT_PROTOCOL_VERSION, 3)

        if self.ldap_url.urlscheme == 'ldaps':
            #FIXME : Proper handling of certificate, or at least
            #FIXME : make the ignore a connection setting ?
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

            self.connection.set_option(ldap.OPT_X_TLS,ldap.OPT_X_TLS_DEMAND)
            self.connection.set_option(ldap.OPT_X_TLS_DEMAND, True )

        self._name = self.ldap_url.unparse()


    def connect(self, user='', password=''):
        try:
            #If the connection string did not include a basedn 
            if self.base == '':
                #We try to find it ourselves
                self.base = rootDSE.get_ldap_base(self.connection, timeout=5)

            if user and password:
                self.connection.simple_bind_s(user, password)
            else:
                #FIXME : We could support anonymous access also...
                raise errors.AuthenticationRequiredException()

            #This is to test the credentials.
            result = self.connection.search_st(self.base, ldap.SCOPE_BASE, timeout=5)

            if result is None or len(result) == 0:
                logging.warning('Got an empty response trying to connect with user {}'.format(user))

        except ldap.INSUFFICIENT_ACCESS:
            logging.error('Access denied to {}'.format(self.ldap_url.unparse()))
            raise errors.AuthenticationRequiredException #Could be a step up
        except ldap.INVALID_CREDENTIALS:
            logging.warning('Invalid credentials provided for user {}'.format(user))
            raise errors.AuthenticationFailedException()
        except ldap.OPERATIONS_ERROR:
            #This exceptions was tested with an ActiveDirectory 2008 R2, functionnal level 2003
            #when making an anonymous search. You shouldn't get here becase the password is
            #explicitely checked before attempting the search 
            logging.warning('Credentials required for {}'.format(self.ldap_url.unparse()))
            raise errors.AuthenticationRequiredException()
        except ldap.LDAPError:
            logging.exception('Unable to connect to {}'.format(self.ldap_url.unparse()))
            raise errors.UnableToConnectException()

        return self

    def disconnect(self):
        try:
            self.connection.unbind_s()
        except ldap.LDAPError:
            #Let the OS handle the close on our side, should not
            #impact the server too much (assuming it is not closed
            #already)
            pass

        return self

    def convert_query(self, query):
        result = ''
        base = self.base

        #convert objectClass first, as it is indexed (most of the time)
        try:
            result = self.convert_query_element('objectClass', query['objectClass'])
    
            del query['objectClass']
            
        except KeyError:
            #We don't care about objectClass, unusual but valid
            pass
            
        #Then metadata
        #each in its own try except block
        #first the rdn
        try:
            rdn = query['mongolito.rdn']
            #FIXME : What if cn is not used (or replaced with uid?)
            result += '(cn={0})'.format(utils.simple_pattern_from_javascript(rdn))
            del query['mongolito.rdn']
        except KeyError:
            pass

        #then the path
        try:
            path = query['mongolito.parent']
            #We are replacing the base
            #Look at something along those lines
            #http://stackoverflow.com/a/14128905/591064
            #For now, we just use the path as the base (which we must flip). We also
            #ignore the leading ^, if present
            base = utils.reverse_path(utils.pattern_from_javascript(path).lstrip('^'))
            del query['mongolito.parent']
        except KeyError:
            pass

        try:
            path = query['mongolito.path']
            #We are replacing the base
            #Look at something along those lines
            #http://stackoverflow.com/a/14128905/591064
            #For now, we just use the path as the base (which we must flip). We also
            #ignore the leading ^, if present
            base = utils.pattern_from_javascript(path).lstrip('^')
            del query['mongolito.path']
        except KeyError:
            pass

        #Convert other attributes
        for k, v in query.items():
            result += self.convert_query_element(k, v)
            
        return base, '(&{0})'.format(result)


    def convert_query_element(self, attribute, value):
        '''Turns a key, value pair into a ldap filter.
        if the value is a list, items will be or'ed.'''
        result = ''

        if isinstance(value, list):
            for v in value:
                result += '({0}={1})'.format(attribute, v)

            result = '(|{0})'.format(result)

        else:
            result += '({0}={1})'.format(attribute, value)

        return result


    def search(self, query = {}, attributes=[]):
        base, query = self.convert_query(copy.deepcopy(query))

        #Async paged search
        result_generator = self.connection.paged_search_ext_s(base, ldap.SCOPE_SUBTREE, query, attrlist=attributes, serverctrls=self.serverctrls)

        for dn,entry in result_generator:
            # process dn and entry
            yield self.sanitize_result(entry, dn)
       

def create_from_uri(uri):
    '''Creates an instance from a named URI. The format is key value pair,
    where the key is the name this input or output will be refered to, and
    the value is a valid MongoDB connection string, as described here :
    http://docs.mongodb.org/manual/reference/connection-string/        

    '''
    future_self = None

    try:
        #See http://stackoverflow.com/a/17667763/591064 for unparse
        future_self = LDAPReader(ldapurl.LDAPUrl(uri).unparse())
    except ValueError:
        pass

    return future_self

#Boilerplate code to register this in the factory
factory.Factory().register(LDAPReader, create_from_uri)

