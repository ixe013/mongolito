#!/usr/bin/python
"""
This is some text about mongolito.
"""
import copy
import getpass
import logging
import sys

import arguments
import main
import insensitivedict
import readCSV
import readLDIF
import readLDAP
import readShelve
import readMongo
import printldif
import saveInMongo
import saveInShelve
import errors

from controls.changetype import ChangeType

__all__ = [
    'initialize',
    'process', 
    'getSourceDestinationUndo' #FIXME : make the passage from name to generator generic
]

def initialize():
    return main.get_connections()

def update_progress(total):
    if total > 1:
        sys.stderr.write('\r{0} objects'.format(total))
    else:
        sys.stderr.write('\r{0} object'.format(total))

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
        source, query, projection = istream

        generator = source.get_search_object(query, projection)
    except ValueError: #Need more than 1 value to unpack
        generator = istream

    #Just to show something if the first object takes a while (they could all be skipped)
    progress(0) 

    try:
        #We don't use enumerate, because we have to tweak the total count
        #each time we skip an object
        num_objects = 0

        for ldapobject in generator:
            #Lets see if we make it to the end of the loop
            object_processed = False

            #FIXME : Generator filtering should be a class
            #Generator does not decide of changetype, rules do
            #removing the changetype disables the half-baked changetype
            #handling code below
            ldapobject.pop('changetype', None)

            #The original ldapobject that will be sent to the methods must not be 
            #modified. It is an interface contract, because technically speaking
            #nothing will break if you do modify the original object. That is, the
            #code does not make that assumption but modifiy the original ldapobject
            #was never tested and could have nasty side effects.
            #Using ldapobject.deepcopy() here would enforce the interface contract, 
            #but would slow down and consume more memory than needed. So I just 
            #alias the variable for now. If needed, I can always add a .deepcopy()
            #later
            original = insensitivedict.InsensitiveDict(ldapobject)

            logging.debug('Processing {}'.format(original['dn']))

            for rules, output, undo in ostream:
                logging.debug('Begining rule loop')

                #The object that we are working on must be deeply copied because
                #anything can happen to it. This can be rather big in terms of 
                #memory usage, when reading large groups for example, but since 
                #we are only processing one object at a time, it wont take that
                #much anyway
                current = insensitivedict.InsensitiveDict(copy.deepcopy(ldapobject))    

                try:
                    for rule in rules:
                        rule.transform(original, current)    

                    logging.debug('Done with the rules. {} --> {}'.format(original['dn'], current['dn']))

                    try:
                        #Remove the metadata
                        del current['mongolito']
                    except KeyError:
                        logging.warning('No metadata found for object {}'.format(current['dn']))
                        pass

                    #Changetype defaults to add, like ldapmodify does, sort of
                    #FIXME : defaults to legacy handling with write
                    changetype = current.get('changetype')

                    if output:
                        logging.debug('About to ouput {}'.format(current['dn']))
                        if changetype==ChangeType.add:
                            for attribute_to_add in current[ChangeType.add]:
                                if attribute_to_add in current:
                                    output.add(original, current)
                                    object_processed = bool(rules) #Count the object as processed only if there are rules attached to it
                        elif changetype==ChangeType.modify:
                            if ChangeType.modify in current.keys():
                                #FIXME There could be nothing to do in the end, should skip the object
                                for attribute_to_modify in current[ChangeType.modify]:
                                    if attribute_to_modify in current:
                                        output.modify(original, current)
                                        object_processed = bool(rules) #Count the object as processed only if there are rules attached to it
                            else:
                                logging.error('Modification type not yet supported')
                                raise NotImplementedError
                        else:
                            #FIXME : Legacy, remove when others are done
                            output.write(original, current)
                            object_processed = bool(rules) #Count the object as processed only if there are rules attached to it

                    if undo:
                        logging.debug('About to emit undo operation for {}'.format(current['dn']))
                        #FIXME : This should be a dict difference, enabling true CRUD undo
                        #See this implementation : https://github.com/hughdbrown/dictdiffer
                        current['changetype'] = 'delete'
                        #but this single line works in most scenarios
                        undo.write(original, current)


                except errors.SkipObjectException:
                    if output:
                        msg = 'Skipped {}'.format(current['dn'])
                        output.comment(msg)
                        logging.info(msg)

            logging.debug('Processing {} finished'.format(original['dn']))

            if object_processed:
                num_objects += 1
                progress(num_objects) 

    except ValueError as ve:
        #ostream parameter incorrect. Should be in the form rules, output, undo.
        #rules is a list, output and undo support the write method. You can always
        #use None for the undo function 
        logging.exception('ostream parameter incorrect. Should be in the form rules, output, undo.')
        
    #FIXME : Should make this polymorphic or better than catching Exception
    except errors.ParsingException as pe:
        #FIXME logging.exception
        print >> sys.stderr, pe

    except UnicodeError as ue:
        #FIXME logging.exception
        print >> sys.stderr, ue
        


def get_input_object(uri):
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

    input_object = None

    for module in input_modules:
        input_object = module.create_from_uri(uri)
        if input_object is not None:
            break
        
    return input_object


def get_output_and_undo_object(output_uri, undo_uri):
    '''
    Creates a destination object, sending the arguments object 
    to it so that it can configure itself 
    '''
    output_modules = [
        printldif,
        saveInMongo,
    ]
    
    output_object = None
    undo_object = None

    for module in output_modules:
        output_object = module.create_from_uri(output_uri)
        if output_object is not None and undo_uri is not None:
            undo_object = module.create_undo_from_uri(undo_uri)
            #We got everything we need
            break

    return output_object, undo_object

    
def getSourceDestinationUndo():
    args = arguments.Arguments()
    args.parse()

    connexions = args.connexions

    source = get_input_object(connexions['input'])
    destination, undo = get_output_and_undo_object(connexions['output'], connexions.get('undo'))

    #FIXME clients have to call start and stop. Is that bad ?
    return source, destination, undo
    

if __name__ == "__main__":
    import main
    main.main()
