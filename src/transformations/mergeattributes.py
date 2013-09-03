import logging

from transformations import BaseTransformation
from transformations.makevaluesunique import MakeValuesUnique

class MergeAttributes(BaseTransformation):
    '''Removes an attribute, regardless of value.

    '''
    def __init__(self, attribute, first, *attributes):
        '''
        Merges the values of any number of attributes into a single one, ensuring
        that each value appears only once.
    
        Destination attribute is overwritten. If you need to preserve it, add it
        to the list of attribute to merge.
        
        >>>merger = MergeAttributes('member', 'equivalentToMe', 'uniqueMember')

        If all of the attributes are empty, the merged attribute will be created 
        and it will be empty. It is valid to merge an attribute with itself. 

        >>>merger = MergeAttributes('member', 'member', 'equivalentToMe', 'uniqueMember')

        Args:
            attribute (string): The name of the attribute that will contain the result
                of the merge.
            first (string): The name of the first attribute to merge.
            *attributes (string): The other names that must be merged.            

        '''
        self.attribute = attribute
        self.attributes = (first,)+attributes

        if not attributes:
            raise TypeError('Need at least one other attribute for a merge')

 
    def transform(self, original, ldapobject):
        #Assume we will end up with a multi-value (which is likely)
        #Makes the code easier to read, and we will fix it before exiting
        merged_values = []

        for attribute in self.attributes:
            #We are about to merge the values from another
            #key, which might not exist. We wrap this call 
            #in another try, so the loop can continue
            try:
                if isinstance(ldapobject[attribute], basestring):
                    merged_values.extend([ldapobject[attribute]])
                else:
                    merged_values.extend(ldapobject[attribute])

                del ldapobject[attribute]

            except KeyError:
                logging.debug('Attribute {} was not merged because it is not present in transformed object named {}'.format(self.attribute, ldapobject['dn']))
                pass

        ldapobject[self.attribute] = merged_values

        #Reuse
        return MakeValuesUnique(self.attribute).transform(original, ldapobject)
