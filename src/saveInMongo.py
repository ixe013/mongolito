import argparse
import bson
import pymongo
import string
 
import utils

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
        #we use it as a spec (criteria) key for update
     
        try:
            #We use a specification so that multiple imports does not
            #create multiple objects. Making the dn the _id also works
            #but it makes everybody in the pipeline aware of the hack.
            spec = { 'dn' : ldapObject['dn'] }
            #Insert private metadata that we will use later
            #The mongolito.parent field allows to sort results so that
            #parents are always created first
            ldapObject['mongolito'] = { 'parent':utils.compute_parent(ldapObject['dn']) ,
                                        'path':utils.compute_path(ldapObject['dn']) ,
                                      }
            #Upsert the object
            self.collection.update(spec, ldapObject, upsert=True)
        except KeyError:
            raise SaveException(-1, 'dn', 'Object does not have a dn attribute')
        except bson.errors.InvalidStringData:
            raise SaveException(-1, 'dn', ldapObject['dn'])


