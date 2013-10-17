#!/usr/bin/python
'''
This code is executed if mongolito is launched from the command line.

It will look for one source named input and another named output. In 
this trivial example, the file a.ldif is simply copied in b.ldif :

python mongolito.py input=a.ldif output=b.ldif
'''

import ConfigParser as configparser
import logging
import os
import stat
import sys

import arguments
import factory
from insensitivedict import InsensitiveDict as idict
import mongolito
import printldif
import readLDIF

#Contants
TYPE = 'type'
INPUT = 'input'
OUTPUT = 'output'
UNDO = 'undo'
URI = 'uri'

__all__ = ['main','type','input','output','undo','uri']

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
    config = configparser.SafeConfigParser(dict_type=idict)

    if args.configuration:
        config.read(args.configuration)

    aliases = []

    #A command line argument will override the configuration file
    #but only for the top level item. 
    for attribute,value in args.connections.items():
        #Alias have alias_name=@connection_name
        if value.startswith('@'):
            #Aliases will be resolved later, after the connection is
            #created
            aliases.append((attribute,value[1:]))
        #Are we defining a new connection
        elif '.' in attribute:
            #We can override a connection's URI with 
            #name.uri=new_uri
            section_name, param = attribute.split('.',1)
            if not config.has_section(section_name):
                config.add_section(section_name)

            config.set(section_name, param, value)
                
        else:
            if not config.has_section(attribute):
                config.add_section(attribute)
                #output and undo are considered outputs 
                if attribute == OUTPUT or attribute == UNDO:
                    config.set(attribute, TYPE, OUTPUT)
                else:
                    #others are input by default
                    config.set(attribute, TYPE, INPUT)

            #The attribute will be the connection name
            #and the value the uri. The type is input
            config.set(attribute, 'uri', value)
            

    god = factory.Factory()

    for connection in config.sections():
        #Get a dict of all the params for that connection
        params = idict(config.items(connection))
        
        #Create the connection
        conn = god.create(params)

        if conn:
            conn.start(params.get('username'), params.get('password'), params.get('description'))

            connections[connection] = conn
        else:
            logging.error('No handler could be created for {}'.format(connection))

    #For each alias found
    for alias in aliases:
        #Alias is a name alias tuple, with the @ striped off
        #Add a reference to an existing object
        try : 
            connections[alias[0]] = connections[alias[1]]
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

