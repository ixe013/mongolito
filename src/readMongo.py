import pymongo
import re

import basegenerator

def convert_query(query):
    '''Converts a mongolito query to a MongoDB query, which is very similar.
    It basically replaces values that are lists with a $in query operator.
    Mongo will handle the rest.
    '''
    result = {}

    for k,v in query.items():
        if isinstance(v, list):
            result[k] = {'$in':v}
        else:
            result[k] = v

    return result
    

class MongoReader(basegenerator.BaseGenerator):

    def __init__(self, host, database, collection):
        self.host = host
        self.database = database
        self.collection = collection


    @staticmethod
    def addArguments(parser):
        group = parser.add_argument_group('Read objects from a MongoDB database')
        group.add_argument("-m",
                          "--mongo", dest="mongoHost",
                          default='localhost',
                          help="The hostname where MongoDB resides")
         
        #Same names as mongoimport
        group.add_argument("-d",
                          "--db", dest="database",
                          default='test',
                          help="The MongoDB database to use")
         
        #Same names as mongoimport
        group.add_argument("-c",
                          "--collection", dest="collection",
                          default='mongolito',
                          help="The MongoDB collection to use")

        return parser


    def connect(self):
        '''Creates a cursor to the supplied MongoDB database'''
        connection = pymongo.MongoClient(self.host)

        #The great thing about Mongo is that neither the database nor the collections
        #need to exist before hand.
        #That's a good thing, right ?
        self.collection = connection[self.database][self.collection]
        return self

    def disconnect(self):
        return self

    @staticmethod
    def create(args):
        return MongoReader(args.mongoHost, args.database, args.collection)


    @staticmethod
    def create_from_uri(name, uri):
        '''Creates an instance from a named URI. The format is key value pair,
        where the key is the name this input or output will be refered to, and
        the value is a valid MongoDB connection string, as described here :
        http://docs.mongodb.org/manual/reference/connection-string/        

        (The name is extracted by the main loop, it is passed separatly)

        '''
        result = None
        try:
            import pymongo

            parsed_uri = pymongo.uri_parser.parse_uri(uri)

            node = parsed_uri['nodelist'][0]

            result = MongoReader('{0}:{1}'.format(node[0], node[1]), parsed_uri['database'], name)

        except ImportError:
            #PyMongo is not installed
            #TODO LOG Warning !!!
            pass

        except pymongo.errors.InvalidURI:
            #Not for us or malformed
            #TODO LOG Information or debug
            pass
        
        return result


    @staticmethod
    def convert_embeeded_regex(query):
        '''Convert JSON style regex to mongo $regex. If a value is
        a dict, this method calls itself with it.

        Search is always case insensitive.

        '''
        #TODO: Change utils.regex_from_javascript to read the trailing i
        #      instead of a flag for case insensitivity
        pattern = re.compile('/(.*)/(i)?')

        for attribute,value in query.iteritems():
            try:
                match = pattern.match(value)
                if match:
                    #Convert JSON style regex to mongo $regex
                    #Search is always case insensitive
                    query[attribute] = { '$regex':re.sub(pattern, r'\1', value) }

                    #Add the case insensitive option if it was specified
                    if not match.group(2) is None:
                        #If we get here, we know that query[attribute] is
                        #a dict with one key, '$regex'.
                        query[attribute]['$options'] = 'i'

            except TypeError:
                if isinstance(value, list):
                    query[attribute] = [MongoReader.convert_embeeded_regex(rule) for rule in value]

        return query


    def search(self, query = {}, attributes=[]):
        '''Thin wrapper over pymongo.collection.find'''

        #Create the query from the syntaxic sugar
        query = MongoReader.convert_embeeded_regex(query)
        
        #We always remove the _id field.
        projection = {'_id':0 }
        #If attributes is not empty, then they will be 
        #added to the projection so that only those will be 
        #returned. If is is empty (the default), this
        #line has no effect
        projection.update(dict.fromkeys(attributes, 1))

        #Remove the MongoDB _id and all of our metadata
        cursor = self.collection.find(query, projection)
        #Sort so that parent show before their childrens
        cursor = cursor.sort('mongolito.parent', pymongo.ASCENDING)
        #And sort children by rdn
        cursor = cursor.sort('mongolito.rdn', pymongo.ASCENDING)

        #The cursor is already iterable, but this method must be
        #iterable itself. This could have worked (and has for some
        #time)
        #return cursor
        #But now that the search method must return a generator, 
        #I make the yield call myself
        for document in cursor:
            #Will return a generator object
            yield document

