import logging
import re

import utils

from transformations import BaseTransformation

class RemoveAttribute(BaseTransformation):
    '''Removes an attribute, regardless of value.

    '''
    def __init__(self, attribute):
        '''
        >>>remover = RemoveAttribute('logintime')

        :attribute the name (or regex) of the attribute from which a value must be removed
        '''
        self.pattern = re.compile(utils.pattern_from_javascript(attribute), flags=re.IGNORECASE)
 
    def transform(self, original, ldapobject):
            try:
                #For all attribute names that match the pattern
                for match in filter(self.pattern.search, ldapobject.keys()):
                    logging.debug('Deleted attribute {} it matched pattern {}'.format(match, self.pattern.pattern))
                    del ldapobject[match]
                    
            except KeyError:
                pass
    
            return ldapobject
