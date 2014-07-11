import logging
import utils

from transformations import BaseTransformation

class TrimValue(BaseTransformation):
    '''Makes sure that no value is longer than a certain length.

    There are certain edge cases where we could cut a utf-8 sequence.
    We don't handle that...
    '''
 
    def __init__(self, attribute, maxlen):
        '''
        >>>renamer = TrimValue('company', 136)

        :maxlen the maximum number of characters to keep.
        '''
        self.attribute = attribute
        self.maxlen = maxlen
 
    def transform(self, original, ldapobject):
        try:
            trimmed = []

            for value in ldapobject[self.attribute]:
                if '__getitem__' in dir(value):
                    logging.debug('Trimmed attribute {} value {} at {} characters'.format(self.attribute, value, self.maxlen))
                    trimmed.append(value[:self.maxlen])
                else:
                    trimmed.append(value)
                    
            ldapobject[self.attribute] = trimmed

        except KeyError:
            #Attribute does not exist in this dict
            pass

        #Return the new object                
        return ldapobject
 
