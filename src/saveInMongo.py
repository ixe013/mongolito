import argparse
import pymongo
import bson
 

def addArguments(parser):
    group = parser.add_argument_group('Import in a MongoDB database')
    group.add_argument("-m",
                      "--mongo", dest="mongoHost",
                      default=None,
                      help="Use a MongoDB to store the results")
     
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

 
def saveInMongo(collection, ldapObject):
    '''Saves the ldapObject in a Mongo database
    '''
    #If there is a DN (should be, but we don't force it)
    if 'dn' in ldapObject.keys():        
        #Use the DN as a MongoDB object ID
        ldapObject['_id'] = ldapObject.pop('dn').lower()
 
    collection.save(ldapObject)

 
class saveInMongoHelper(object):
    'Binds the collection to make the insertion a one parameter call'
    def __init__(self, collection):
        self.collection = collection

    def __call__(self, ldapObject):
        return saveInMongo(self.collection, ldapObject)


def createMongoOutput(host, database, collection):
    'Returs a callable object that will save ldap objects to a Mongo database'
    connection = pymongo.MongoClient(host)

    #The great thing about Mongo is that neither the database nor the collections
    #need to exist before hand.
    #That's a good thing, right ?
    collection = connection[database][collection]

    return saveInMongoHelper(collection)


def createMongoOutputFromArgs(args):
    return createMongoOutput(args.mongoHost, args.database, args.collection)


