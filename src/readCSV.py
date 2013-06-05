'''
Reads in a bunch of CSV entries, making a dict out of each line.

'''
import csv
import argparse


class CSVReader(object): 
    def __init__(self, ldiffile, delimiter, innerseparator):
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

    def search(self, query = {}):
        for ldapobject in csv.DictReader(self.ldiffile, delimiter=self.delimiter):
            for key, value in ldapobject.iteritems():
                if self.innerseparator in value:
                    ldapobject[key] = value.split(self.innerseparator)
            
            yield ldapobject


