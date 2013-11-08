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

        If all of the attributes are empty, the merged attribute will not be 
        created.

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
        #For all attributes we have to merge
        for attribute in self.attributes:
            #We are about to merge the values from another
            #key, which might not exist. We wrap this call 
            #in another try, so the loop can continue
            ldapobject.setdefault(self.attribute, [])

            try:
                ldapobject[self.attribute].extend(ldapobject[attribute])

                if ldapobject[self.attribute]:
                    #Reuse
                    MakeValuesUnique(self.attribute).transform(original, ldapobject)

                del ldapobject[attribute]

            except KeyError:
                logging.debug('Attribute {} was not merged because it is not present in transformed object named {}'.format(attribute, ldapobject['dn']))

            finally:
                #Don't leave an empty attribute behind
                if not ldapobject[self.attribute]:
                    del ldapobject[self.attribute]

        return ldapobject
