#!/usr/bin/python
"""
This is some text about mongolito.
"""
import argparse
import pymongo
import sys

import readLDIF
import printldif
import saveInMongo
import importExceptions


def addArguments(parser):
    parser.add_argument("-i",
                      "--input", dest="inputType",
                      choices=['ldif','mongo'],
                      help="The source or format of record(s) to transform.")

    parser.add_argument("-o",
                      "--output", dest="outputType",
                      choices=['ldif','mongo'],
                      help="The destination and format of transformed record(s).")

    return parser


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


def old_main(args):
    num_objects = 0

    output = None

    if args.mongoHost is not None:
        output = saveInMongo.createMongoOutputFromArgs(args)    
    else:
        output = printldif.createPrintOutput(args)

    try:
        for ldapObject in ldifExtractionIterator(args.ldiffile):
            output(ldapObject)
            num_objects += 1

    except importExceptions.LDIFParsingException as lpe:
        print >> sys.stderr, lpe

    except UnicodeError as ue:
        print >> sys.stderr, ue
        
    print >> sys.stderr, num_objects, 'objects imported.'


def createArgumentParser():
    '''Default argument parsing. Allows the developper to configure the 
    transformation engine along with their code'''
    parser = argparse.ArgumentParser()

    parser = addArguments(parser)
     
    #Ask each module to add their arguments
    parser = readLDIF.addArguments(parser)
    parser = saveInMongo.addArguments(parser)
     
    return parser


def createInputSource(args):
    '''Creates a source object, sending the arguments object 
    to it so that it can configure itself '''
    inputSource = None

    #Create the proper input object
    if args.inputType == 'ldif':
        #LDIF input, create and configure
        inputSource = ldifInputFormat(args)
    elif args.inputType == 'mongo':
        #Mongodb input, create and configure
        #TODO
        pass

    return inputSource


def createOutputDestination(args):
    '''Creates a destination object, sending the arguments object 
    to it so that it can configure itself '''
    destination = None

    #Create the proper output object
    if args.outputType == 'ldif':
        destination = printldif.createPrintOutput(args)
    elif args.outputType == 'mongo':
        destination = saveInMongo.createMongoOutputFromArgs(args)    
    
    return destination

    
def getSourceDestination():
    '''Returns the source and destination object as a tuple'''
    parser = createArgumentParser()

    args = parser.parse_args()

    source = createInputSource(args)
    destination= createOutputDestination(args)

    return source, destination
    

def main():
    source, destination = getSourceDestination()
    old_main(source, destination)


if __name__ == "__main__":
    main()
