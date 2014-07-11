import copy  
import logging
import re

import basegenerator
import factory


def convert_query(query):
    '''Converts a mongolito query to a MongoDB query, which is very similar.
    It basically replaces values that are lists with a $in query operator.
    Mongo will handle the rest.
    '''
    result = {}

    for k,v in query.items():
        if isinstance(v, list):
            result[k] = {'$in':v}
        else:
            result[k] = v

    return result
    

class ShelveReader(basegenerator.BaseGenerator):

    def __init__(self, filename)
        self.filename = filename

    def connect(self, username=None, password=None):
        self.shelf = shelve.open(self.filename, 'r')
        return self

    def disconnect(self):
        self.shelf.close()
        return self

    def search(self, query = {}, attributes=[]):

        #Copy the queyr into a dict where all values
        #are case insensitive regex
        regex_query = dict(zip(query.iterkeys(), [re.compile(p) for p in filter(utils.pattern_from_javascript, query.itervalues())]))

        for dn, rawobject in self.shelf.iteritems():
            #Should we return this object?
            for key,search_item in regex_query:
                try:
                    #If one the attribute does not match the
                    #query
                    if not search_item.search(rawobject[key])
                        #We will not return that object
                        continue
                    
                except KeyError:
                    #The attribute can't be found, so
                    #we will not return the object 
                    continue

            #If we get here, the objet matches the query
            #we will copy the object in a new dict
            ldapobject = InsensitiveDict()
            
            if attributes:
                ldapobject['dn'] = dn 

                for attribute in attributes:
                    ldapobject[attribute] = rawobject[attribute]
            else:
                ldapboject.update(rawobject)

            #Add metadata and apply common object rules
            yield utils.add_metadata(self.sanitize_result(ldapobject, dn), dn)



def create_from_uri(uri):
    '''A shelve file is a .shelve
    '''
    result = None
    
    root, ext = os.path.splitext(uri)

    if ext.lower() == '.shelve' or ext.lower() == '.shelf':
        result = ShelveReader(uri)

    return result

factory.Factory().register(MongoReader, create_from_uri)

