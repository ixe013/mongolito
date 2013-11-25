import itertools
import logging 
import re

import utils

from . import BaseTransformation

#import pdb; pdb.set_trace()

#This is just to differentiate from an int
#based value
class PlaceHolderForGroup(int):
    pass

#TODO : document this class
class ValuesFromQuery(BaseTransformation):
    '''Renames a value with the result of a sub query

    '''
    def __init__(self, attribute, pattern, query, source, cache=False, selected='dn'):
        '''
        '''
        self.attribute = attribute
        self.pattern = re.compile(utils.pattern_from_javascript(pattern), flags=re.IGNORECASE)
        self.query = query
        self.source = source
        self.selected = selected

        self.cache_enabled = False  #Cache default is OFF
        self.cache = {}
        
        #Reusing an external cache is better
        if isinstance(cache, dict):
            self.cache_enabled = True
            self.cache = cache
        elif cache:
            self.cache_enabled = True

        self.cache['__hits'] = self.cache.get('__hits', 0)
        self.cache['__miss'] = self.cache.get('__miss', 0)
       

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
            values = [group.lower() for group in match.groups()]
            results = []

            if self.cache_enabled:
                #Prime the results with the cache 
                results = [self.cache[key] for key in set(values) & set(self.cache)]
                
                if results:
                    logging.debug('Cache hit for values {}'.format(values))
                    #Add the count of object found to the hit count
                    self.cache['__hits'] += len(values)  
                    #Remove the values found in the cache from the values to query
                    values = list(set(values) - set(self.cache))

            #If there are values that were not found in the cache
            if values:
                #We must translate any place holders
                query = self.set_query_values(values)

                self.cache['__miss'] += len(values)  
                logging.info('Cache miss for {}'.format(values))

                #Build an array of values. Most of the time, only
                #one result will be returned
                new_results = self.source.get_attribute(query, self.selected)
                
                if new_results:
                    results.extend(new_results)
                else:
                    logging.warning('Subquery failed for {}'.format(values))

                if self.cache_enabled:
                    #Add the new results to the cache, along with the entries not found
                    self.cache.update(dict(zip(values, new_results or itertools.repeat(None))))

        else:
            #Return the original value untouched
            results = [attribute]

        #Filter out None (those mean that we have a cache 
        #hit, but the subquery did not find anything)
        return [x for x in results if x is not None]

        
    def transform(self, original, ldapobject):
        '''
        :ldapobject a dictionary reprenting one entry
        '''
        try:
            results = []
            
            #For each value of the attribute we want to replace
            for value in ldapobject[self.attribute]:
                results.extend(self.execute_query(value))

            if results:
                ldapobject[self.attribute] = results
            else:
                #We delete the attribute if it is empty
                del ldapobject[self.attribute]
            
        except KeyError:
            #The attribute we want to replace is absent from ldapobject
            pass

        #Return the object, possibly modified                
        return ldapobject

