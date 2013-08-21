import logging 
import re

import utils

from . import BaseTransformation

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
            values = match.groups()
            results = []

            if self.cache_enabled:
                #Prime the results with the cache 
                results = [self.cache[key.lower()] for key in set(values) & set(self.cache)]
                
                #Add the count of object found to the hit count
                self.cache['__hits'] += len(results)  

                #Remove the values found in the cache from the values to query
                values = list(set(values) - set(self.cache))

            #If there are values that were not found in the cache
            if values:
                #We must translate any place holders
                query = self.set_query_values(values)

                self.cache['__miss'] += len(values)  

                #Build an array of values. Most of the time, only
                #one result will be returned
                new_results = [r for r in self.source.get_attribute(query, self.selected)]
                
                results.extend(new_results)

                if self.cache_enabled:
                    #Add the new results to the cache
                    self.cache.update(dict(zip([v.lower() for v in values], new_results)))

            #The subquery did not find anything
            if not results:
                for v in values:
                    #Cache the failure
                    self.cache[v.lower()] = None
                    logging.warn('{0} not found in subquery'.format(v))

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

