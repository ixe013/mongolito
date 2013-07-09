import ldap
import ldap.resiter
import ldapurl
import re
import utils

class LDAPObjectStream(ldap.ldapobject.LDAPObject, ldap.resiter.ResultProcessor):
    pass

def convert_raw_ldap_result(dn, raw):
    result = {}

    result['dn'] = dn

    for k,v in raw.items():
        if len(v) == 1:
            result[k] = v[0]
        else:
            result[k] = v

    return result

        
class LDAPReader(object):

    def __init__(self, uri):
        #FIXME : try and handle ValueError ?
        ldap_url = ldapurl.LDAPUrl(uri)

        #Will be use to understand queries with mongolito metadata later
        self.base = ldap_url.dn

        #Encoding is not automatic, for some reason
        regex = re.compile("^<(.*)>(.*)<(.*)>$")
        r = regex.search(ldap_url.htmlHREF())
        uri = r.group(2)

        self.connection = LDAPObjectStream(uri)

        if ldap_url.urlscheme == 'ldaps':
            #FIXME : Proper handling of certificate, or at least
            #FIXME : make the ignore a connection setting
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

            self.connection.set_option(ldap.OPT_REFERRALS, 0)
            self.connection.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
            self.connection.set_option(ldap.OPT_X_TLS,ldap.OPT_X_TLS_DEMAND)
            self.connection.set_option(ldap.OPT_X_TLS_DEMAND, True )


    @staticmethod
    def addArguments(parser):
        return parser


    @staticmethod
    def create(args):
        return LDAPReader(args.uri)

    def connect(self, user, password):
        self.connection.simple_bind_s(user, password)
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

    @staticmethod
    def create_from_uri(name, uri):
        '''Creates an instance from a named URI. The format is key value pair,
        where the key is the name this input or output will be refered to, and
        the value is a valid MongoDB connection string, as described here :
        http://docs.mongodb.org/manual/reference/connection-string/        

        '''
        parsed_url = ldapurl.LDAPUrl(uri)

        #Encoding is not automatic, for some reason
        regex = re.compile("^<(.*)>(.*)<(.*)>$")
        r = regex.search(parsed_url.htmlHREF())
        uri = r.group(2)

        return LDAPReader(uri)

        
    def get_attribute(self, query={}, attribute = 'dn', error=KeyError):
        '''Returns an iterator over a single attribute from a search'''
        for ldapobject in self.search(query, [attribute]):
            try:
                yield ldapobject[attribute]
            except KeyError as ke:
                if error is not None:
                    raise ke

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
            result += '(|(cn={0})(uid={0})(ou={0}))'.format(rdn)
            del query['mongolito.rdn']
        except KeyError:
            pass

        #then the path
        try:
            path = query['mongolito.path']
            #'/^c=ca,st=qc,o=hydro-quebec,ou=applications,ou=sap,ou=codes_applic/',
            #'^c=ca,st=qc,o=hydro-quebec,ou=applications,ou=sap,ou=codes_applic',
            #We are replacing the base
            #Look at something along those lines
            #http://stackoverflow.com/a/14128905/591064
            #For now, we just use the path as the base (which we must flip). We also
            #ignore the leading ^, if present
            base = utils.reverse_path(utils.pattern_from_javascript(path).lstrip('^'))
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
        base, query = self.convert_query(query)

        #Async search
        msg_id = self.connection.search(base, ldap.SCOPE_SUBTREE, query, attrlist=attributes)

        #allresults is a generator
        for res_type,res_data,res_msgid,res_controls in self.connection.allresults(msg_id):
            for dn,entry in res_data:
                # process dn and entry
                yield convert_raw_ldap_result(dn, entry)
       
