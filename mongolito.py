import argparse
import pymongo
import sys

import readLDIF
import printldif
import saveInMongo
import importExceptions


def ldifExtractionIterator(input_stream, lineCount=0):
    '''This generator pulls strings from the input_stream until a terminating
    blank line is found'''
    while True:
        #Read the next object
        c, lines = readLDIF.extractLDIFFragment(input_stream, lineCount)

        #If an object was found
        if len(lines) > 0:
            #convert the raw lines to a Python dict 
            ldapObject = readLDIF.convertLDIFFragment(lines)
            lineCount += c

            #return that object
            yield ldapObject

        #Reached the end of the input stream
        else:
            break


def main(args):
    num_objects = 0

    output = None

    if args.useMongo:
        output = saveInMongo.createMongoOutputFromArgs(args)    
    else:
        output = printldif.createPrintOutput(args)

    try:
        for ldapObject in ldifExtractionIterator(args.ldiffile):
            output(ldapObject)
            num_objects += 1

    except importExceptions.LDIFParsingException as lpe:
        print >> sys.stderr, lpe

        
    print >> sys.stderr, num_objects, 'objects imported.'


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
     
    #Ask each module to add their arguments
    parser = readLDIF.addArguments(parser)
    parser = saveInMongo.addArguments(parser)
     
    #Parse the command line
    main(parser.parse_args())


