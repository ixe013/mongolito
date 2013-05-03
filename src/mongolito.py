#!/usr/bin/python
"""
This is some text about mongolito.
"""
import argparse
import pymongo
import sys

import daisychain
import readLDIF
import readMongo
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


def update_progress(total):
    sys.stderr.write('\r{0} objects'.format(total))


def process(source, filters, transformations, output):
    '''Somewhat generic loop. Could be refactored to filter, but
    that would require to keep the list in memory.'''
    num_objects = 0

    pipeline = daisychain.Pipeline(transformations)

    try:
        for ldapObject in pipeline(source.searchRecords(filters)):
            output.write(ldapObject)
            num_objects += 1
            update_progress(num_objects)

    #FIXME : Should make this polymorphic or better than catching Exception
    except importExceptions.LDIFParsingException as lpe:
        print >> sys.stderr, lpe

    except UnicodeError as ue:
        print >> sys.stderr, ue
        
    if num_objects > 0:
        print >> sys.stderr, ' -- done'

    return num_objects


def createArgumentParser():
    '''Default argument parsing. Allows the developper to configure the 
    transformation engine along with their code'''
    parser = argparse.ArgumentParser()

    parser = addArguments(parser)
     
    return parser


def getInputClass(args):
    '''Creates a source object, sending the arguments object 
    to it so that it can configure itself '''
    inputSource = None

    #Returns the class to use
    if args.inputType == 'ldif':
        #LDIF input, create and configure
        inputSource = readLDIF.LDIFReader
    elif args.inputType == 'mongo':
        #Mongodb input, create and configure
        inputSource = readMongo.MongoReader

    return inputSource


def getOutputClass(args):
    '''Creates a destination object, sending the arguments object 
    to it so that it can configure itself '''
    destination = None

    #Create the proper output object
    if args.outputType == 'ldif':
        destination = printldif.LDIFPrinter
    elif args.outputType == 'mongo':
        destination = saveInMongo.MongoWriter
    
    return destination

    
def getSourceDestination():
    '''Returns the source and destination object as a tuple'''
    parser = createArgumentParser()

    #Start with the top level argument group, which will
    #tell which end talks to which other end
    args, other_args = parser.parse_known_args()

    #Create both end of the process
    source = getInputClass(args)
    destination = getOutputClass(args)

    #Ask each end to add their arguments
    parser = source.addArguments(parser)
    parser = destination.addArguments(parser)

    #Retreive the values for the new arguments
    args = parser.parse_args(other_args)

    return source.create(args), destination.create(args)
    

def main():
    source, destination = getSourceDestination()
    n = process(source, {}, [], destination)


if __name__ == "__main__":
    main()
