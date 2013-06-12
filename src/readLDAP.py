import re

class LDAPReader(object):

    def __init__(self, host, database, collection):
        pass


    @staticmethod
    def addArguments(parser):
        return parser


    @staticmethod
    def create(args):
        return MongoReader('', args.mongoHost, args.database, args.collection)


    @staticmethod
    def create_from_uri(name, uri):
        '''Creates an instance from a named URI. The format is key value pair,
        where the key is the name this input or output will be refered to, and
        the value is a valid MongoDB connection string, as described here :
        http://docs.mongodb.org/manual/reference/connection-string/        

        '''
        result = None
        try:
            import ldap


        except ImportError:
            #python-ldap is not installed
            #TODO LOG Warning !!!
            pass

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

