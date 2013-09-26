#!/usr/bin/python
'''
This code is executed if mongolito is launched from the command line.

It will look for one source named input and another named output. In 
this trivial example, the file a.ldif is simply copied in b.ldif :

python mongolito.py input=a.ldif output=b.ldif
'''

import ConfigParser as configparser
import logging
import sys

import arguments
import factory
from insensitivedict import InsensitiveDict as idict
import mongolito
import nestedconfigdict
import printldif
import readLDIF

__all__ = ['main']

args = arguments.Arguments()

def is_stdin_redirected():
    '''
    Returns True if stdin appears to be either redirected or piped
    Adapted from http://stackoverflow.com/a/13443424/591064
    '''
    mode = os.fstat(0).st_mode
    return stat.S_ISFIFO(mode) or stat.S_ISREG(mode)

def get_connections():
    '''Creates a dict of connections found in the configuration file or
    on the command line. Each dict key is a string and a ready to use
    input or output connection.
    
    It will read alias for the input and ouput well known connections.

    If no input is given but stdin is redirected, a LDIFReader on stdin
    will be created. If no ouput is given, a LDIFPrint will be created,
    just in case.
    '''
    args.parse()

    connections = idict({})
    config = configparser.SafeConfigParser()

    if args.configuration:
        config.read(args.configuration)

    try:
        #Use the first section name, any name
        section_name = config.sections()[0]

        #A command line argument will override the configuration file
        #but only for the top level item. 
        for k,v in args.connections.items():
            config.set(section_name, k, v)

    except IndexError:
        section_name = None


    #boot strap the connections with what is in the file
    connections = nestedconfigdict.get_top_level_config_elements(config, idict)

    god = factory.Factory()

    aliases = []
    for connection, uri in connections.items():
        if uri.startswith('@'):
            #We will handle alias later
            aliases.append(connection)
        else:
            #Get a dict of all the params for that connection
            params = nestedconfigdict.get_nested_config_elements(config, connection, idict)
            
            #Get the type. If none is provided but the name is input,
            #consider it as an input. All other cases are outputs
            conn = god.create(uri, params.get('type','').lower()=='input')

            if conn:
                conn.start(params.get('username'), params.get('password'), params.get('description'))

                connections[connection] = conn
            else:
                logging.error('No handler could be created for {}'.format(uri))

    #For each alias found
    for alias in aliases:
        target = connections[alias][1:]
        #Add a reference to an existing object
        try : 
            connections[alias] = connections[target]
        except KeyError: 
            logging.error('Alias {} requested for non-existing configuration named {}'.format(alias, target))

    if 'input' not in connections and is_stdin_redirected():
        #Throw in a defautl LDIF output
        connections.update({'input':readLDIF.LDIFReader().start()})

    if 'output' not in connections:
        #Throw in a defautl LDIF output
        connections.update({'output':printldif.LDIFPrinter().start()})

    return connections
        

def main():
    result = -1

    connections = mongolito.initialize()

    if 'input' in connections:
        source = connections['input']
        destination = connections['output']
        undo = connections.get('undo')

        query = { 'objectClass':'*' } #Could be quite large
        mongolito.process((source, query, []), [([], destination, undo)])

        if undo: undo.stop()
        if destination: destination.stop()
        source.stop()
    else:
        print >> sys.stderr, 'You must specify one source as an input'

    return result


if __name__ == '__main__':
    main()

