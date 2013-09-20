#!/usr/bin/python
'''
This code is executed if mongolito is launched from the command line.

It will look for one source named input and another named output. In 
this trivial example, the file a.ldif is simply copied in b.ldif :

python mongolito.py input=a.ldif output=b.ldif
'''

import arguments
import factory
import insensitivedict

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

    connections['input'].start()
    connections['input'].stop()

   #source, destination, undo = getSourceDestinationUndo()
   #
   #source.start()
   #
   ##FIXME : Make destinations startable (connect) and stoppable (disconnect)
   #destination.connect()
   #
   #process((source, {}, []), [([], destination, undo)])
   #
   #source.stop()

    return result


if __name__ == '__main__':
    main()

