'''
Reads in a bunch of CSV entries, making a dict out of each line.

'''
import csv
import argparse


class CSVReader(object): 
    def __init__(self, ldiffile):
        self.ldiffile = ldiffile


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
        #The line count is there just to put in the Exception record if something
        #goes wrong.
        lineCount = 0

        for ldapobject in csv.DictReader(self.ldiffile)
            lineCount = lineCount+1
            yield ldapobject

        return lineCount


