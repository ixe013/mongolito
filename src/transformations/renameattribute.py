import re

import utils

from transformations import BaseTransformation

class RenameAttribute(BaseTransformation):
    '''Takes a key name and renames it, keeping values intact.

    Uses Python's re.sub(), so fancy renames with expression
    groups can be used.
    '''
 
    def __init__(self, attribute, replacement):
        '''
        >>>renamer = RenameAttribute('(.*)bar', r'blah\1')

        :pattern A valid PCRE pattern
        :replacement A string (than can refer to the pattern with expression groups)
        '''
        self.attribute = attribute
        self.replacement = replacement
 
    def transform(self, original, ldapobject):
        try:
            ldapobject[self.replacement] = ldapobject[self.attribute]
            del ldapobject[self.attribute]
        except KeyError:
            #Attribute does not exist in this dict
            pass

        #Return the new object                
        return ldapobject
 
