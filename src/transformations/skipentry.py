import re

import utils

from transformations import BaseTransformation, errors

class SkipEntry(BaseTransformation):
    '''Renames a value with a regular expression pattern.

    Each value in multi-valued attributes are tested for 
    a match and renamed if necessary.

    '''
    def __init__(self, attribute, pattern):
        '''
        >>>renamer = SkipEntry('dn', '/.*ou=AAA.*/')

        :attribute the name of the attribute from which a value must be removed
        '''
        self.attribute = attribute
        self.pattern = re.compile(utils.pattern_from_javascript(pattern), flags=re.IGNORECASE)
 
    def transform(self, original, ldapobject):
        '''
        :data a dictionary reprenting one entry
        '''
        try:
            value = utils.get_nested_attribute(ldapobject, self.attribute)

            #If the attribute is multi-valued
            if isinstance(value, list): 
                if any(self.pattern.search, value):
                    raise errors.SkipEntryException
            #If the attribute is a string
            elif isinstance(value, basestring):
                if self.pattern.search(value):
                    raise errors.SkipObjectException
                    
        except KeyError:
            #The attribute name is not a regex, so there can only be
            #one match.
            pass

        #Return the object, possibly modified                
        return ldapobject
 

