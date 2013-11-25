'''
Reads in a bunch of CSV entries, making a dict out of each line.

'''
import csv
import os

import basegenerator
import factory

class CSVReader(basegenerator.BaseGenerator):
    def __init__(self, ldiffile, delimiter=';', innerseparator='|'):
        self.ldiffile = ldiffile
        self.delimiter = delimiter
        self.innerseparator = innerseparator

    def search(self, query = {}):
        for ldapobject in csv.DictReader(self.ldiffile, delimiter=self.delimiter):
            for key, value in ldapobject.iteritems():
                if self.innerseparator in value:
                    ldapobject.setdefault(key, []).extend(value.split(self.innerseparator))
                else:
                    ldapobject.setdefault(key, []).append(self.attribute)
            
            #FIXME : query is ignored, should be sent through a generic 
            #post processing filter
            yield self.sanitize_result(ldapobject)


def create_from_uri(uri):
    '''Creates an instance from a named URI. The format is key value pair,
    where the key is the name this input or output will be refered to, and
    the value is a valid MongoDB connection string, as described here :
    http://docs.mongodb.org/manual/reference/connection-string/        

    (The name is extracted by the main loop, it is passed separatly)

    '''
    result = None
    
    root, ext = os.path.splitext(uri)

    if ext.lower() in ['.csv', '.txt']:
        result = CSVReader(uri)

    return result


factory.Factory().register(CSVReader, create_from_uri)
