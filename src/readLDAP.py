import ldap
import ldapurl
import re

class LDAPReader(object):

    def __init__(self, uri, user, password):
        #FIXME : try and handle ValueError ?
        uri.replace(',','%2c')
        ldap_url = ldap.LDAPUrl(uri)
        self.base = ldap_url.dn

        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

        self.connection = ldap.ldapobject.LDAPObject('{0}://{1}:{2}'.format('ldaps',host, 636))

        self.connection.set_option(ldap.OPT_REFERRALS, 0)
        self.connection.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
        self.connection.set_option(ldap.OPT_X_TLS,ldap.OPT_X_TLS_DEMAND)
        self.connection.set_option(ldap.OPT_X_TLS_DEMAND, True )

        self.connection.simple_bind_s(user, password)


    @staticmethod
    def addArguments(parser):
        return parser


    @staticmethod
    def create(args):
        return LDAPReader(args.uri)

    def release(self):
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
        result = None

        return result

        
    def get_attribute(self, query={}, attribute = 'dn', error=KeyError):
        '''Returns an iterator over a single attribute from a search'''
        for ldapobject in self.search(query, [attribute]):
            try:
                yield ldapobject[attribute]
            except KeyError as ke:
                if error is not None:
                    raise ke


    def search(self, query = {}, attributes=[]):
        '''Thin wrapper over pymongo.collection.find'''
        pass

