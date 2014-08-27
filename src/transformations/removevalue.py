import re

import utils

from transformations import BaseTransformation

class RemoveValue(BaseTransformation):
    '''Removes a value from an attribute, deleting it when the last value is removed.

    If the value is the last one for the attribute, the attribute 
    is deleted. When removing from a list, if there is a single attribute 
    left after the operation, it keeps only the object, (value = value[0])

    '''
    def __init__(self, attribute, value):
        '''
        >>>remover = RemoveValue('objectClass', 'irrelevant')
        >>>remover = RemoveValue('objectClass', '/^irrelevant.*expression$/')

        :attribute the name of the attribute from which a value must be removed
        :value the value to be removed. Can be a regular expression enclosed in //
        '''
        self.attribute = attribute
        self.pattern = re.compile(utils.pattern_from_javascript(value), flags=re.IGNORECASE)
 
    def transform(self, original, ldapobject):
        '''
        :data a dictionary reprenting one entry
        '''
        try:
            #The set of attributes, minus the set of attributes that don't match the pattern
            #converted to a list is the new value for the attribute
            ldapobject[self.attribute] = list(set(ldapobject[self.attribute])-set(filter(self.pattern.search, ldapobject[self.attribute])))
                    
            if not ldapobject[self.attribute]:
                del ldapobject[self.attribute]

        except KeyError:
            #The attribute name is not present in the dict
            #so there is nothing to do
            pass

        #Return the object, possibly modified                
        return ldapobject
 
