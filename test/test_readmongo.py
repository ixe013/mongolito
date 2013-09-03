import unittest

import pymongo

import readMongo

class MyTest(unittest.TestCase):
    def testParseURI(self):
        mr = readMongo.MongoReader.create_from_uri('test','coucou')
        self.assertIsNone(mr)

        mr = readMongo.MongoReader.create_from_uri('test','mongodb://127.0.0.1:1/asdf')
        self.assertIsNotNone(mr)

    def testConnection(self):
        mr = readMongo.MongoReader.create_from_uri('test','mongodb://127.0.0.1:1/asdf')
        with self.assertRaises(pymongo.errors.ConnectionFailure):
            mr.connect()

    def testConvertQuery(self):
        query = {
            'objectClass':['userProxyFull','user'],
            'description':'Hello*',
            'mongolito.rdn':'Dude',
            'mongolito.path':'/^dc=com,dc=example/',
        }

        expected = {
            'objectClass':{'$in':['userProxyFull','user']},
            'description':'Hello*',
            'mongolito.rdn':'Dude',
            'mongolito.path':'/^dc=com,dc=example/',
        }

        self.assertEquals(expected, readMongo.convert_query(query))

if __name__ == "__main__":
    unittest.main()
