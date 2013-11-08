import logging
import re

import utils

from transformations import BaseTransformation
import errors

class SkipEntry(BaseTransformation):
    """Skips entries whose value(s) match a regular expression
    for a given attribute.

    """
    def __init__(self, attribute, pattern, reverse=False):
        """
        Stops processing (and moves to the next ldap object) if
        a value matches the pattern or not. 

        >>>skipper = SkipEntry('dn', '/.*ou=AAA.*/')

        Args:
            attribute (string): the name of the attribute from which a value must be removed
            pattern (string): a regex pattern (can be in javascript format /(.*)/) to search
                in the attribute value(s). Search is always case-insensitive. 
            revers (boolean): If true, non-matching entries will be skipped.
        """
        self.attribute = attribute
        self.pattern = pattern
        self.reverse = reverse
 
    def transform(self, original, ldapobject):
        """
        :data a dictionary reprenting one entry
        """
        value = utils.get_nested_attribute(ldapobject, self.attribute)

        #regex are cached, let's use that to our advantage
        pattern = re.compile(utils.pattern_from_javascript(self.pattern), flags=re.IGNORECASE)

        #If the attribute is multi-valued
        if isinstance(value, list): 
            if self.reverse ^ bool(any(pattern.search, value)):
                logging.debug('Skipped {} because {} matched pattern {}'.format(ldapobject['dn'], self.attribute, self.pattern))
                raise errors.SkipObjectException
        else: #the attribute is a string
            if self.reverse ^ bool(pattern.search(value)) :
                logging.debug('Skipped {} because {} matched pattern {}'.format(ldapobject['dn'], self.attribute, self.pattern))
                raise errors.SkipObjectException
                    
        logging.debug('{} was not skipped because {} did not match pattern {}'.format(ldapobject['dn'], self.attribute, self.pattern))

        #Return the object
        return ldapobject
 

