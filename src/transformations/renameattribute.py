import re

import utils

from transformations import BaseTransformation

class RenameAttribute(BaseTransformation):
    '''Takes a key name and renames it, keeping values intact.

    Uses Python's re.sub(), so fancy renames with expression
    groups can be used.
    '''
 
    def __init__(self, pattern, replacement):
        '''
        >>>renamer = RenameAttribute('(.*)bar', r'blah\1')

        :pattern A valid PCRE pattern
        :replacement A string (than can refer to the pattern with expression groups)
        '''
        self.pattern = re.compile(utils.pattern_from_javascript(pattern), flags=re.IGNORECASE)
        self.replacement = replacement
 
    def transform(self, ldapobject):
        '''
        :data a dictionary reprenting one entry
        '''
        #Copy over to a new dict is easier
        transformed = {}
    
        #For each key value pair in the orginal dict
        for attribute,value in ldapobject.iteritems():
            #Save a transformed key value pair.
            #Values (even complex ones) are untouched
            #re.sub will not change attribute names that don't match
            #Does not check if a key with the same name already 
            #exists or try to merge with it
            transformed[re.sub(self.pattern, self.replacement, attribute)] = value

        #Return the new object                
        return transformed
 
