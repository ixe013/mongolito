#!/usr/bin/python
"""
This is some text about mongolito.
"""
import argparse
import copy
import logging
import sys
import time

import insensitivedict
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



def process(istream, ostream, showprogress=True):
    '''
    This is the core routine for object transformation.
    istream might be a tuple make of a query and a source or be an iterable
    object by itself.

    The ostream parameter is a list of 3-tuples:
    (rules, output, undo)
    Where rules is a list of transformation objects, ouput and undo are objects 
    that has a write(dict) method. Undo can be None if no undo file is required.

    '''

    progress = update_progress
    #Eat progress if none is required
    if not showprogress :
        progress = lambda x: None

    try:
        generator = istream[0].get_search_object(istream[1], istream[2])    
    except AttributeError:
        generator = istream

    try:
        for num_objects, ldapobject in enumerate(generator):
            for rules, output, undo in ostream:
                #The original ldapobject that will be sent to the methods must not be 
                #modified. It is an interface contract, because technically speaking
                #nothing will break if you do modify the original object. Using 
                #ldapobject.deepcopy() here would enforce the interface contract, but
                #but would slow down and consume more memory than needed. So I just 
                #alias the variable for now. If needed, I can always add a .deepcopy()
                #later
                original = insensitivedict.InsensitiveDict(ldapobject)

                #The object that we are working on must be deeply copied because
                #anything can happen to it. This can be rather big in terms of 
                #memory usage, when reading large groups for example, but since 
                #we are only processing one object at a time, it wont take that
                #much anyway
                current = insensitivedict.InsensitiveDict(copy.deepcopy(ldapobject))    

                for rule in rules:
                    rule.transform(original, current)    

                    try:
                        #Remove the metadata
                        del current['mongolito']
                    except KeyError:
                        #TODO warning if logging is info or debug
                        pass

                output.write(original, current)

                if undo is not None:
                    undo.write(original, current)

            num_objects += 1
            progress(num_objects)

    except ValueError as ve:
        #ostream parameter incorrect. Should be in the form rules, output, undo.
        #rules is a list, output and undo support the write method. You can always
        #use None for the undo function 
        print >> sys.stderr, ve
        
    #FIXME : Should make this polymorphic or better than catching Exception
    except importExceptions.LDIFParsingException as lpe:
        print >> sys.stderr, lpe

    except UnicodeError as ue:
        print >> sys.stderr, ue
        

def generate(istream, ostream):
    def yielder(x):
        yield x

    for rules, output, undo in ostream:
        process(istream, (rules, yielder, None))

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

    source.connect()
    destination.connect()

    process((source, {}, []), [([], destination, None)])

    destination.disconnect()
    source.disconnect()


if __name__ == "__main__":
    main()
