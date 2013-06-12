import unittest

import pymongo

import readMongo
import importExceptions

class MyTest(unittest.TestCase):
    def testParseURI(self):
        mr = readMongo.MongoReader.create_from_uri('test','coucou')
        self.assertIsNone(mr)

        with self.assertRaises(pymongo.errors.ConnectionFailure):
            mr = readMongo.MongoReader.create_from_uri('test','mongodb://127.0.0.1:1/asdf')


if __name__ == "__main__":
    unittest.main()
