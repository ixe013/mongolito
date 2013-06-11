import pymongo
import re

class MongoReader(object):

    def __init__(self, host, database, collection):
        '''Creates a cursor to the supplied MongoDB database'''
        connection = pymongo.MongoClient(host)

        #The great thing about Mongo is that neither the database nor the collections
        #need to exist before hand.
        #That's a good thing, right ?
        self.collection = connection[database][collection]


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


    @staticmethod
    def create(args):
        return MongoReader(args.mongoHost, args.database, args.collection)

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

        #The cursor is already iterable, return it
        return cursor

