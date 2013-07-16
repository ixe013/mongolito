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
import readCSV
import readLDIF
import readLDAP
import readMongo
import printldif
import saveInMongo
import importExceptions


def addArguments(parser):
    parser.add_argument("-i", "--input", default='stdin',
                      help="The source URI (file name, ldap or mongo URI) of record(s) to transform. Defaults to read LDIF from stdin")

    parser.add_argument("-o", "--output", default='stdout',
                      help="The destination URI (file name, ldap or mongo URI) of transformed record(s). Defaults to ouput LDIF to stdout")

    parser.add_argument("-z", "--undo",
                      help="The undo file name. The same output class as output will be used.")

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


def getInputClass(uri):
    '''
    Creates a source object, sending the arguments object 
    to it so that it can configure itself 
    '''
    input_modules = [
        readLDIF,
        readMongo,
        readLDAP,
        readCSV,
    ]

    input_class = None

    for cls in input_modules:
        input_class = cls.create_from_uri(uri)
        if input_class is not None:
            break
        
    return input_class


def getOutputClass(uri):
    '''
    Creates a destination object, sending the arguments object 
    to it so that it can configure itself 
    '''
    output_modules = [
        printldif,
        saveInMongo,
    ]
    
    output_class = None

    for cls in output_modules:
        output_class = cls.create_from_uri(uri)
        if output_class is not None:
            break

    return output_class

    
def getSourceDestination():
    initialize_logging()

    '''Returns the source and destination object as a tuple'''
    parser = createArgumentParser()

    #Start with the top level argument group, which will
    #tell which end talks to which other end
    args = parser.parse_args()

    #Create both end of the process
    source = getInputClass(args.input)
    destination = getOutputClass(args.output)

    #FIXME clients have to call connect and disconnect. Is that bad ?
    return source, destination
    
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
