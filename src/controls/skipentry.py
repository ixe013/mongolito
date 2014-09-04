import inspect 
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
        (frame, self.rule_filename, self.rule_line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]

        self.attribute = attribute
        self.pattern = re.compile(utils.pattern_from_javascript(pattern), flags=re.IGNORECASE)
        self.reverse = reverse
 
    def transform(self, original, ldapobject):
        """
        :data a dictionary reprenting one entry
        """
        try:
            value = utils.get_nested_attribute(ldapobject, self.attribute)

            #regex are cached, let's use that to our advantage
            #(we keep the original pattern as a string to put it in the logs)

            #If the attribute is multi-valued
            if isinstance(value, list): 
                if self.reverse ^ bool(any(filter(self.pattern.search, value))):
                    logging.info('Skipped {} because one of {}={} matched pattern {} (rule at {}:{})'.format(ldapobject['dn'], self.attribute, ldapobject.get(self.attribute), self.pattern.pattern, self.rule_filename, self.rule_line_number))
                    raise errors.SkipObjectException
            else: #the attribute is a string (should not happen, all attributes are lists even if there is only one item)
                if self.reverse ^ bool(pattern.search(value)) :
                    logging.info('Skipped {} because {} matched pattern {}'.format(ldapobject['dn'], self.attribute, self.pattern.pattern))
                    raise errors.SkipObjectException
                        
            #We don't have a match so we should keep it, unless it is opposite day. Either way, the attribute stays
            if self.reverse:
                logging.debug('{} was not skipped because {}={} matched pattern {} (rule at {}:{})'.format(ldapobject['dn'], self.attribute, ldapobject.get(self.attribute), self.pattern.pattern, self.rule_filename, self.rule_line_number))
            else:
                logging.debug('{} was not skipped because {}={} did not match pattern {} (rule at {}:{})'.format(ldapobject['dn'], self.attribute, ldapobject.get(self.attribute), self.pattern.pattern, self.rule_filename, self.rule_line_number))

        except KeyError:
            #A missing attribute is not a match. But if we are in reverse mode, 
            #then it becomes one.
            if self.reverse:
                raise errors.SkipObjectException


        #Return the object
        return ldapobject
 

