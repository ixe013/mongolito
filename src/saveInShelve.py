import bson
import logging
import os
import shelve
import string
 
import factory
import basedestination
import utils

class SaveException(Exception):
    def __init__(self, line, dn, message):
        self.line = line
        self.message = message
        self.dn = dn

    def __str__(self):
        return 'Error line %d "%s" : %s' % (self.line, self.dn, self.message)

class ShelveWriter(basedestination.BaseDestination):
    def __init__(self, filename):
        self.filename = filename

    def connect(self):
        self.shelf = shelve.open(self.filename)
        return self
 
    def disconnect(self):
        self.shelf.close()
        return self
 
    def write(self, original, ldapobject):
        '''Saves the ldapobject in a Mongo database
        '''
        try:
            dn = ldapobject['dn'][0]

            if isinstance(dn, unicode):
                dn = dn.encode('utf-8')

            utils.add_metadata(ldapobject, dn)
            
            self.shelf[dn] = dict(zip(ldapobject.keys(), ldapobject.values()))

        except KeyError:
            raise SaveException(-1, 'dn', 'Object does not have a dn attribute')


def create_from_uri(uri):
    '''A shelve file is a .shelve
    '''
    result = None
    
    root, ext = os.path.splitext(uri)

    if uri == 'stdin' or ext.lower() == '.shelve':
        result = ShelveWriter(uri)

    return result

factory.Factory().register(ShelveWriter, create_from_uri)
