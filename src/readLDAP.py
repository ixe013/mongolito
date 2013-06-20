import ldap
import ldapurl
import re
import utils

class LDAPReader(object):

    def __init__(self, uri):
        #FIXME : try and handle ValueError ?
        ldap_url = ldapurl.LDAPUrl(uri)

        #Will be use to understand queries with mongolito metadata later
        self.base = ldap_url.dn
        self.user = ldap_url.who
        self.password = ldap_url.cred

        #Encoding is not automatic, for some reason
        regex = re.compile("^<(.*)>(.*)<(.*)>$")
        r = regex.search(ldap_url.htmlHREF())
        uri = r.group(2)

        self.connection = ldap.ldapobject.LDAPObject(uri)

        if ldap_url.urlscheme == 'ldaps':
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

    def connect(self):
        self.connection.simple_bind_s(self.user, self.password)

    def disconnect(self):
        try:
            self.connection.unbind_s()
        except ldap.LDAPError:
            #Let the OS handle the close on our side, should not
            #impact the server too much (assuming it is not closed
            #already)
            pass

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

        #convert objectClass first
        try:
            classes = query['objectClass']

            if isinstance(classes, list):
                for objclass in classes:
                    result += '(objectClass={0})'.format(objclass)
            else:
                result += '(objectClass={0})'.format(classes)
    
            del query['objectClass']
            
        except KeyError:
            #We don't care about objectClass, unusual but valid
            pass
            
        #Then metadata
        #each in its own try except block
        #first the rdn
        try:
            rdn = query['mongolito.rdn']
            result += '(|(cn={0})(uid={0}))'.format(rdn)
        except KeyError:
            pass

        #then the path
        try:
            path = query['mongolito.path']
            #'/^c=ca,st=qc,o=hydro-quebec,ou=applications,ou=sap,ou=codes_applic/',
            temp_base = utils.pattern_from_javascript(path) 
            #'^c=ca,st=qc,o=hydro-quebec,ou=applications,ou=sap,ou=codes_applic',
            #We are replacing the base
            #Look at something along those lines
            #http://stackoverflow.com/a/14128905/591064
            
        except KeyError:
            pass

        #Convert other attributes
        for k, v in query.items():
            if isinstance(v, list):
                for objclass in v:
                    result += '({0}={1})'.format(k, objclass)
            else:
                result += '({0}={1})'.format(k,v)
            
        return base, r'(&{0})'.format(result)

    def search(self, query = {}, attributes=[]):
        '''Thin wrapper over pymongo.collection.find'''
        pass

