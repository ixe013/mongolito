#!/usr/bin/python
'''
This code is executed if mongolito is launched from the command line.

It will look for one source named input and another named output. In 
this trivial example, the file a.ldif is simply copied in b.ldif :

python mongolito.py input=a.ldif output=b.ldif
'''

import sys

import arguments
import factory
import insensitivedict
import mongolito
import printldif

__all__ = ['main']

args = arguments.Arguments()

def get_connections():
    '''Creates a dict of connections from the command line.'''
    args.parse()
    connections = insensitivedict.InsensitiveDict({})
    god = factory.Factory()

    for name,uri in args.connections.items():
        connections[name] = god.create(uri)

    return connections
        

def main():
    result = -1

    connections = get_connections()

    if 'input' in connections :
        source = connections['input']
        source.start()
        if 'output' in connections :
            destination = connections['output']
        else:   
            destination = printldif.LDIFPrinter()

        destination.start()
        query = { 'objectClass':'*' } #Could be quite large
        mongolito.process((source, query, []), [([], destination, None)])
        destination.stop()
        source.stop()
    else:
        print >> sys.stderr, 'You must specify one source as an input'

    return result


if __name__ == '__main__':
    main()

