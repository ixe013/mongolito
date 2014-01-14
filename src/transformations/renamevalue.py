import re

import utils

from transformations import BaseTransformation

class RenameValue(BaseTransformation):
    '''Renames a value with a regular expression pattern.

    Each value in multi-valued attributes are tested for 
    a match and renamed if necessary.

    '''
    def __init__(self, attribute, pattern, replacement):
        '''
        >>>renamer = RenameValue('dn', '/.*ou=AAA.*/', r'\1ou=BBB\2')

        :attribute the name of the attribute from which a value must be removed
        '''
        self.attribute = attribute
        self.pattern = re.compile(utils.pattern_from_javascript(pattern), flags=re.IGNORECASE)
        self.replacement = replacement
 
    def transform(self, original, ldapobject):
        '''
        :data a dictionary reprenting one entry
        '''
        try:
            value = ldapobject[self.attribute]

            ldapobject[self.attribute] = [re.sub(self.pattern, str(self.replacement), v) for v in value]

            #Extract and break appart the first component of the dn, so that
            #first_component will be ['ou', 'people'] (for example)
            first_component = ldapobject['dn'][0].split(',',1)[0].split('=')

            #Smart handling of the dn attribute
            if self.attribute == 'dn':
                #Split all the components by comma, 
                #then split the first one by equal sign
                #so dc=www,dc=example,dc=com will change
                #{ 'dc':'www' } in ldapobject
                #DOCS: Mention that smart handling of dn will overrite multi-values
                ldapobject[first_component[0]] = [first_component[1]]
                    
        except KeyError:
            #The attribute name is not a regex, so there can only be
            #one match.
            pass
        except TypeError as te:
            raise te

        #Return the object, possibly modified                
        return ldapobject
 

