import re

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
        results = []
        #Try the pattern
        match = self.pattern.search(attribute)
        #If it matches
        if match:
            #We must translate any place holders
            query = self.set_query_values(match.groups())

            #Build an array of values
            results = [r for r in self.source.get_attribute(query, self.selected)]

        return results
        
    def transform(self, ldapobject):
        '''
        :ldapobject a dictionary reprenting one entry
        '''
        try:
            results = []
            #TODO single valued attribute
            if isinstance(ldapobject[self.attribute], basestring):
                results = self.execute_query(ldapobject[self.attribute])
            else:
                #For each value of the attribute we want to replace
                for value in ldapobject[self.attribute]:
                    results.extend(self.execute_query(value))

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
 

