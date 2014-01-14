import re

import utils

from transformations import BaseTransformation

class ChangeCase(BaseTransformation):
    '''Changes the case of text that match a 
    regular expression pattern. 

    Pattern are case sensitive.

    Pattern can be arbitrary complex. Put the parts
    that you want the case changed in groups. The case
    of all groups will be changed. If you need to do both
    uppercase and lowercase transformation, use 2 ChangeCase
    transformations (one for each).

    Each value in multi-valued attributes are tested for 
    a match and case-changed if necessary.

    '''
    UPPER = 1
    LOWER = 2
    #TOGGLE = 3   #TODO
    #CAMEL = 4    #TODO

    def __init__(self, attribute, pattern, change):
        '''
        >>>case_changer = ChangeCase('dn', '/cn=([a-z]{2}).*/', ChangeCase.UPPER)

        :attribute the name of the attribute from which a value must be removed
        '''
        self.attribute = attribute
        self.pattern = re.compile(utils.pattern_from_javascript(pattern))
        self.change = change
 
    def _identity(self, match):
        return match.group()

    def _upper(self, match):
        return match.group().upper()

    def _lower(self, match):
        return match.group().lower()

    def get_case_changer(self):
        if self.change == self.UPPER:
            return self._upper
        elif self.change == self.LOWER:
            return self._lower
        else:
            return self._identity
        
    def transform(self, original, ldapobject):
        '''
        :data a dictionary reprenting one entry
        '''
        try:
            value = ldapobject[self.attribute]

            ldapobject[self.attribute] = [re.sub(self.pattern, self.get_case_changer(), v) for v in value]

            #Smart handling of the dn attribute
            if self.attribute == 'dn':
                #Extract and break appart the first component of the dn, so that
                #first_component will be ['ou', 'people'] (for example)
                first_component = ldapobject['dn'][0].split(',',1)[0].split('=')

                #Split all the components by comma, 
                #then split the first one by equal sign
                #so dc=www,dc=example,dc=com will change
                #{ 'dc':'www' } in ldapobject
                #TODO Mention in the documentation that smart handling of dn will overrite multi-values
                ldapobject[first_component[0]] = [first_component[1]]
                    
        except KeyError:
            #The attribute name is not a regex, so there can only be
            #one match.
            pass

        #Return the object, possibly modified                
        return ldapobject

