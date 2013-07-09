import logging 
import re
import sys

import utils

from transformations import BaseTransformation

#This is just to differentiate from an int
#based value
class PlaceHolderForGroup(int):
    pass

#TODO : document this class
class ValuesFromQuery(BaseTransformation):
    '''Renames a value with the result of a sub query

    '''
    def __init__(self, attribute, pattern, query, source, selected='dn'):
        '''
        '''
        self.attribute = attribute
        self.pattern = re.compile(utils.pattern_from_javascript(pattern), flags=re.IGNORECASE)
        self.query = query
        self.source = source
        self.selected = selected
 
    def set_query_values(self, groups):
        #We must reverse lookup the fields to replace
        #in the query dict we received

        #Leave the original query intact
        query = dict(self.query)

        for key, param in self.query.iteritems():
            if isinstance(param, PlaceHolderForGroup):
                #This could be a regular expression, but it is too slow
                query[key] = groups[param-1]

        return query
        
    def execute_query(self, attribute):
        '''Runs the sub query.
        Running the sub query means that the attribute we must work with was
        present in the object were we sent to transform. 
        Now :
        1. We see if the attribute's value matches a pattern we have to lookup 
        2. From the previous match, we have a bunch of groups.
        3. Replace each placeholder with the corresponding group
        4. call get_attribute (which is a search that returns an array)
        '''
        #We only lookup original values that match
        #the supplied pattern
        match = self.pattern.search(attribute)

        if match:
            #We must translate any place holders
            query = self.set_query_values(match.groups())

            #Build an array of values. Most of the time, only
            #one result will be returned
            results = [r for r in self.source.get_attribute(query, self.selected)]
            
            if not results:
                logging.warn('{0} not found in subquery'.format(attribute))
        else:
            results = [attribute]

        return results
        
    def transform(self, original, ldapobject):
        '''
        :ldapobject a dictionary reprenting one entry
        '''
        try:
            results = []
            
            value = ldapobject[self.attribute]
            if isinstance(value, basestring):
                results = self.execute_query(value)
            else:
                #For each value of the attribute we want to replace
                for v in value:
                    results.extend(self.execute_query(v))

            if not results:
                #We delete the attribute if it is empty
                del ldapobject[self.attribute]
            elif len(results) == 1:
                #Or make it single valued
                ldapobject[self.attribute] = results[0]
            else:
                #or save it as is
                ldapobject[self.attribute] = results
            
        except KeyError:
            #The attribute we want to replace is absent from ldapobject
            pass

        #Return the object, possibly modified                
        return ldapobject

