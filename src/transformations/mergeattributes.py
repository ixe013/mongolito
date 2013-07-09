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
        >>>merger = MergeAttributes('member', 'member', 'equivalentToMe', 'uniqueMember')

        :attribute the name of the attribute to merge to
        :attributes a variable lenght list of attribute names that must be merged

        '''
        self.attribute = attribute
        self.attributes = (first,)+attributes

        if not attributes:
            raise TypeError('Need at least one other attribute for a merge')

 
    def transform(self, original, ldapobject):
        try:
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
                    pass

            ldapobject[self.attribute] = merged_values

        except KeyError:
            pass

        #Reuse
        return MakeValuesUnique(self.attribute).transform(original, ldapobject)
