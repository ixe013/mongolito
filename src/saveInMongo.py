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
            
            #FIXME : metadata should be centralised and generated regardless of source
            ldapobject['mongolito'] = { 'parent':utils.compute_parent(ldapobject['dn']) ,
                                        'path':utils.compute_path(ldapobject['dn']) ,
                                      }
            
            #Best effort guess to choose a rdn : first of cn or uid
            try:
                ldapobject['mongolito']['rdn'] = ldapobject['cn'].lower()
            except KeyError:
                try:
                    ldapobject['mongolito']['rdn'] = ldapobject['uid'].lower()
                except KeyError:
                    #TODO use first component, like OU or DC?
                    pass

            
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


