import copy
import logging
import os
import re
import shelve

import basegenerator
import factory
import insensitivedict
import utils



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

    def __init__(self, filename):
        self.filename = filename

    def connect(self, username=None, password=None):
        self.shelf = shelve.open(self.filename, 'r')
        return self

    def disconnect(self):
        self.shelf.close()
        return self

    def ldapobjectMatchesQuery(self, rawobject, regex_query):
        '''Will return True if the rawobject matches all of the parameters of the query'''

        #Feeling optimistic today...
        found = True

        #Should we return this object?
        for key, search_item in regex_query.iteritems():
            try:
                #If none of the attribute does not match the query
                #FIXME : metadata is not multivalued, so it introduces a special case
                #FIXME : the fix would be to make metadata multivalued. 
                value_to_test = utils.get_nested_attribute(rawobject, key)

                if isinstance(value_to_test, list):
                    if not any(filter(search_item.search, value_to_test)):
                        #We will not return that object
                        found = False
                        break
                else:
                    if not search_item.search(value_to_test):
                        #We will not return that object
                        found = False
                        break
                
            except KeyError:
                #The attribute can't be found, so
                #we will not return the object 
                found = False
                break

        return found


    def prepareRawobjectForYield(self, dn, rawobject, attributes):
        ldapobject = insensitivedict.InsensitiveDict({})
        
        if attributes:
            ldapobject['dn'] = dn 

            for attribute in attributes:
                ldapobject[attribute] = rawobject[attribute]
        else:
            ldapboject.update(rawobject)

        return ldapobject

    def search(self, query = {}, attributes=[]):

        #Copy the queyr into a dict where all values
        #are case insensitive regex
        regex_query = dict(zip(query.iterkeys(), [re.compile(p, re.IGNORECASE) for p in filter(utils.pattern_from_javascript, query.itervalues())]))

        #Can we save a table scan?
        #We have an index, but it will work only if there is no regex
        #Let's try it blindly
        try:
            dn = regex_query['dn'].pattern.lower()

            if dn in self.shelf.keys():
                rawobject = self.shelf[dn]
                #Found it! (or else we would be in the KeyError handler)
                #The object was not save with the metadata, so let's make sure its there
                utils.add_metadata(self.sanitize_result(rawobject, dn), dn)
                yield self.prepareRawobjectForYield(rawobject['dn'], rawobject, attributes)

        except KeyError:
            #Our only key is not in the query
            #no choice but to do a table scan
            for dn, rawobject in self.shelf.iteritems():
                #The object was not save with the metadata, so let's make sure its there
                utils.add_metadata(self.sanitize_result(rawobject, dn), dn)

                if self.ldapobjectMatchesQuery(rawobject, regex_query):
                    #If we get here, the objet matches the query
                    #we will copy the object in a new dict
                    yield self.prepareRawobjectForYield(dn, rawobject, attributes)


def create_from_uri(uri):
    '''A shelve file is a .shelve
    '''
    result = None
    
    root, ext = os.path.splitext(uri)

    if ext.lower() == '.shelve' or ext.lower() == '.shelf':
        result = ShelveReader(uri)

    return result

factory.Factory().register(ShelveReader, create_from_uri)

