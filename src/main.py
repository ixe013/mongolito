#!/usr/bin/python
'''
This code is executed if mongolito is launched from the command line.

It will look for one source named input and another named output. In 
this trivial example, the file a.ldif is simply copied in b.ldif :

python mongolito.py input=a.ldif output=b.ldif
'''

import argparse

__all__ = ['main']

def main():
    result = -1

    source, destination, undo = getSourceDestinationUndo()

    source.connect()
    destination.connect()

    process((source, {}, []), [([], destination, undo)])

    destination.disconnect()
    source.disconnect()

    return result

if __name__ == '__main__':
    return main()

