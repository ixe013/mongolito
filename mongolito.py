import argparse
import pymongo
import sys

import ldif2dict
import printldif
import saveInMongo
import importExceptions


#TODO Maybe we should move this to its own file ^
parser = argparse.ArgumentParser()
 
parser.add_argument("-f",
                  "--file", dest="filename",
                  help="The LDIF file to import")
 
parser.add_argument("-m",
                  "--mongo", dest="useMongo",
                  action="store_true",
                  help="Use a MongoDB to store the results")
 
#Same names as mongoimport
parser.add_argument("-d",
                  "--db", dest="database",
                  default='test',
                  help="The MongoDB database to use")
 
#Same names as mongoimport
parser.add_argument("-c",
                  "--collection", dest="collection",
                  default='mongolito',
                  help="The MongoDB collection to use")
 

 
#Parse the command line
args = parser.parse_args()


def ldifExtractionIterator(input_stream, lineCount=0):
    '''This generator pulls strings from the input_stream until a terminating
    blank line is found'''
    while True:
        #Read the next object
        c, lines = ldif2dict.extractLDIFFragment(input_stream, lineCount)

        #If an object was found
        if len(lines) > 0:
            #convert the raw lines to a Python dict 
            ldapObject = ldif2dict.convertLDIFFragment(lines)
            lineCount += c

            #return that object
            yield ldapObject

        #Reached the end of the input stream
        else:
            break


def main():
    input_stream = sys.stdin

    num_objects = 0

    if not args.filename == None:
        input_stream = open(args.filename, "r")

    output = None

    if args.useMongo:
        output = saveInMongo.createMongoOutputFromArgs(args)    
    else:
        output = printldif.createPrintOutput(args)

    try:
        for ldapObject in ldifExtractionIterator(input_stream):
            output(ldapObject)
            num_objects += 1

    except importExceptions.LDIFParsingException as lpe:
        print >> sys.stderr, lpe

        
    if args.filename != None:
        input_stream.close()

    print >> sys.stderr, num_objects, 'objects imported.'

if __name__ == "__main__":
    main()

