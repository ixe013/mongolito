'''
Reads in a bunch of CSV entries, making a dict out of each line.

'''
import argparse
import csv
import os


class CSVReader(object): 
    def __init__(self, ldiffile, delimiter=';', innerseparator='|'):
        self.ldiffile = ldiffile
        self.delimiter = delimiter
        self.innerseparator = innerseparator

    @staticmethod
    def addArguments(parser):
        group = parser.add_argument_group('Import CSV file')
        group.add_argument("-x",
                          "--csv", dest="csvfile",
                          type=argparse.FileType('r'),
                          help="The CSV file to import. Use - for stdin")

        return parser


    @staticmethod
    def create(args):
        return CSVReader(args.ldiffile)

    #FIXME : should be in base class, mixin or similar
    def connect(self):
        return self

    #FIXME : should be in base class, mixin or similar
    def disconnect(self):
        return self

    @staticmethod
    def create_from_uri(name, uri):
        '''Creates an instance from a named URI. The format is key value pair,
        where the key is the name this input or output will be refered to, and
        the value is a valid MongoDB connection string, as described here :
        http://docs.mongodb.org/manual/reference/connection-string/        

        (The name is extracted by the main loop, it is passed separatly)

        '''
        result = None
        
        root, ext = os.path.splitext(uri)

        if ext.lower() in ['.csv', '.txt']:
            result = CSVReader(uri)

        return result


    def search(self, query = {}):
        for ldapobject in csv.DictReader(self.ldiffile, delimiter=self.delimiter):
            for key, value in ldapobject.iteritems():
                if self.innerseparator in value:
                    ldapobject[key] = value.split(self.innerseparator)
            
            yield ldapobject


