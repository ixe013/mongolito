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


    def searchRecords(self, query = {}):
        '''Thin wrapper over pymongo.collection.find'''
        #Convert javascript style regular expressions to $regex format.
        #Pymongo style $regex will be left alone
        pattern = re.compile('/(.*)/')
        #>>> re.sub(pattern, r"{ '$regex':'\1' }", jsre)
        for attribute,value in query.iteritems():
            try:
                if pattern.match(value):
                    #Convert JSON style regex to mongo $regex
                    #Search is always case insensitive
                    query[attribute] = { '$regex':re.sub(pattern, r'\1', value), '$options':'i' }
            except TypeError:
                #Beg for forgiveness
                pass
        
        
        #Create the query
        #Remove the MongoDB _id and all of our metadata
        cursor = self.collection.find(query,{'_id':0, 'mongolito':0})
        #Sort so that parent show before their childrens
        cursor = cursor.sort('mongolito.parent', pymongo.ASCENDING)

        #The cursor is already iterable
        return cursor

