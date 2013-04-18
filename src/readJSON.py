import pymongo
 
def readJSON(collection, ldapObject):
    '''Reads and output the ldapObject in a Mongo database
    '''
    #If there is a DN (should be, but we don't force it)
    if 'dn' in ldapObject.keys():        
        #Use the DN as a MongoDB object ID
        ldapObject['_id'] = ldapObject.pop('dn').lower()
 
    collection.save(ldapObject)

 
class readJSONHelper(object):
    'Binds the collection to make the insertion a one parameter call'
    def __init__(self, collection):
        self.collection = collection

    def __call__(self, ldapObject):
        return readJSON(self.collection, ldapObject)


def createJSONInput(database, collection):
    'Returs a callable object that will save ldap objects to a Mongo database'
    connection = pymongo.MongoClient()

    #The great thing about Mongo is that neither the database nor the collections
    #need to exist before hand.
    #That's a good thing, right ?
    collection = connection[database][collection]

    return readJSONHelper(collection)


def createMongoInputFromArgs(args):
    return createJSONInput(args.database, args.collection)


if __name__ == "__main__":
    main()

