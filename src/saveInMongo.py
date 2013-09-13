import bson
import pymongo
import string
 
import baseproducer
import utils

class SaveException(Exception):
    def __init__(self, line, dn, message):
        self.line = line
        self.message = message
        self.dn = dn

    def __str__(self):
        return 'Error line %d "%s" : %s' % (self.line, self.dn, self.message)


class MongoWriter(baseproducer.BaseProducer):
    def __init__(self, host, database, collection):
        'Returs a callable object that will save ldap objects to a Mongo database'
        connection = pymongo.MongoClient(host)

        #The great thing about Mongo is that neither the database nor the collections
        #need to exist before hand.
        #That's a good thing, right ?
        self.collection = connection[database][collection]


    def convert_to_mongo_datatype(self, value):
        '''Makes sure that value(s) are in a datatype that Mongo will accept.

        Converts byterray to Binary, recursing into lists
        
        '''
        if isinstance(value, list):
            value = [self.convert_to_mongo_datatype(v) for v in value]
        elif isinstance(value, bytearray):
            value = bson.binary.Binary(str(value))

        return value

    def connect(self):
        return self
 
    def disconnect(self):
        return self
 
    def write(self, original, ldapobject):
        '''Saves the ldapobject in a Mongo database
        '''
        #If there is a DN (should be, but we don't force it)
        #we use it as a spec (criteria) key for update
     
        try:
            #We use a specification so that multiple imports does not
            #create multiple objects. Making the dn the _id also works
            #but it makes everybody in the pipeline aware of the hack.
            spec = { 'dn' : ldapobject['dn'] }
            #Insert private metadata that we will use later
            #The mongolito.parent field allows to sort results so that
            #parents are always created first
            
            utils.add_metadata(ldapobject, ldapobject['dn'])
            
            #I though there would be an implict conversion to dict, but
            #there is not. Let's make one.
            #This line works in most cases :
            #ldapobject = dict(zip(ldapobject.keys(), ldapobject.values()))
            #But Mongo will fail to insert any binary objects that are in 
            #ldapobject.values(). The zip statement above can be written in
            #a single line, but the following is clearer imo
            mongoobject = {}

            for attribute, value in ldapobject.iteritems():
                mongoobject[attribute] = self.convert_to_mongo_datatype(value)

            #Upsert the object
            self.collection.update(spec, mongoobject, upsert=True)

        except KeyError:
            raise SaveException(-1, 'dn', 'Object does not have a dn attribute')
        except bson.errors.InvalidDocument:
            raise SaveException(-1, ldapobject['dn'], 'Encoding the object returned an invalid BSON document')
        except bson.errors.InvalidStringData:
            raise SaveException(-1, ldapobject['dn'], 'Object has a value that is not properly encoded')


def create_from_uri(uri):
    '''Creates an instance from a named URI. The format is key value pair,
    where the key is the name this input or output will be refered to, and
    the value is a valid MongoDB connection string, as described here :
    http://docs.mongodb.org/manual/reference/connection-string/        

    (The name is extracted by the main loop, it is passed separatly)

    '''
    result = None

    try:
        import pymongo

        try:
            mongo_uri, name = uri.rsplit('#',1)
        except ValueError:
            logging.error('Append the collection name at the end of the URI, with a #, like this: {0}#collection'.format(uri))
            raise pymongo.errors.InvalidURI(uri)

        parsed_uri = pymongo.uri_parser.parse_uri(mongo_uri)

        node = parsed_uri['nodelist'][0]

        result = MongoWriter('{0}:{1}'.format(node[0], node[1]), parsed_uri['database'], name)

    except ImportError:
        #PyMongo is not installed
        #TODO LOG Warning !!!
        pass

    except pymongo.errors.InvalidURI:
        #Not for us or malformed
        #TODO LOG Information or debug
        pass
    
    return result

def create_undo_from_uri(uri):
    #TODO
    return None
