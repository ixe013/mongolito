import argparse
import pymongo
import bson
 

class SaveException(Exception):
    def __init__(self, line, dn, message):
        self.line = line
        self.message = message
        self.dn = dn

    def __str__(self):
        return 'Error line %d "%s" : %s' % (self.line, self.dn, self.message)


class MongoWriter(object):
    def __init__(self, host, database, collection):
        'Returs a callable object that will save ldap objects to a Mongo database'
        connection = pymongo.MongoClient(host)

        #The great thing about Mongo is that neither the database nor the collections
        #need to exist before hand.
        #That's a good thing, right ?
        self.collection = connection[database][collection]


    @staticmethod
    def create(args):
        return MongoWriter(args.mongoHost, args.database, args.collection)

    @staticmethod
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

 
    def write(self, ldapObject):
        '''Saves the ldapObject in a Mongo database
        '''
        #If there is a DN (should be, but we don't force it)
        if 'dn' in ldapObject.keys():        
            #Use the DN as a MongoDB object ID
            ldapObject['_id'] = ldapObject.pop('dn').lower()
     
        try:
            self.collection.save(ldapObject)

        except bson.errors.InvalidStringData:
            raise SaveException(-1, 'dn', ldapObject['_id'])


