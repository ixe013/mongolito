#!/usr/bin/python
"""
This is some text about mongolito.
"""
import argparse
import logging
import sys
import time

import insensitivedict
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

    parser.add_argument("-q",
                      "--quiet", dest="quiet",
                      action='store_true',
                      help="Do not display progress.")

    return parser


def update_progress(total):
    sys.stderr.write('\r{0} objects'.format(total))


def process(source, query, attributes, transformations, output, progress=update_progress):
    '''Somewhat generic loop. Could be refactored to filter, but
    that would require to keep the list in memory.'''
    num_objects = 0

    pipeline = daisychain.Pipeline(transformations)

    #Eat progress if none is required
    if progress is None:
        progress = lambda x: None

    try:
        for ldapObject in pipeline(source.search(query, attributes)):
            try:
                #Remove the metadata
                del ldapObject['mongolito']
            except KeyError:
                pass
            output.write(insensitivedict.InsensitiveDict(ldapObject))
            num_objects += 1
            progress(num_objects)

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
    initialize_logging()

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

    if args.quiet:
        update_progress = lambda x: None

    #FIXME clients have to call connect and disconnect. Is that bad ?
    return source.create(args), destination.create(args)
    
def initialize_logging():
    logging.basicConfig(filename=time.strftime('mongolito.%Y-%m-%d.%Hh%M.log'), level=logging.INFO)    

def main():
    source, destination = getSourceDestination()
<<<<<<< HEAD
    process(source, {}, [], [], destination)
=======

    source.connect()
    destination.connect()

    process(source, {}, [], destination)
>>>>>>> 90e81a9e3b3911710aa306c9787cfa6df54cf7cb

    destination.disconnect()
    source.disconnect()


if __name__ == "__main__":
    main()
