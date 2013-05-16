import re

import utils

from transformations import BaseTransformation

class RemoveValue(BaseTransformation):
    '''Removes a value from an attribute, deleting it when the last value is removed.

    If the value is the last one for the attribute, the attribute 
    is deleted. When removing from a list, if there is a single attribute 
    left after the operation, it keeps only the object, (value = value[0])

    '''
    def __init__(self, attribute, value):
        '''
        >>>remover = RemoveValue('objectClass', 'irrelevant')

        :attribute the name of the attribute from which a value must be removed
        :value the value to be removed. Can be a regular expression enclosed in //
        '''
        self.attribute = attribute
        self.pattern = re.compile(utils.pattern_from_javascript(value), flags=re.IGNORECASE)
 
    def transform(self, ldapobject):
        '''
        :data a dictionary reprenting one entry
        '''
        #For each dictionary object to process
        #For each key value pair in the orginal dict
        for attribute,value in ldapobject.iteritems():
            if attribute == self.attribute:
                #If the attribute is multi-valued
                if isinstance(value, list): 
                    #Remove the value
                    new_value = filter(lambda v: not self.pattern.search(v), value)
                    #Make a single item list into that item
                    if len(new_value)==1:
                        ldapobject[attribute] = new_value[0]
                    #Delete the attribute if it was the last item
                    elif len(new_value)==0:
                        del ldapobject[attribute]
                    #Or save the remaining items from the list
                    else:
                        ldapobject[attribute] = new_value

                #If the attribute is a string
                elif isinstance(value, basestring):
                    if self.pattern.search(value):
                        del ldapobject[attribute]

                #The attribute name is not a regex, so there can only be
                #one match.
                break

        #Return the object, possibly modified                
        return ldapobject
 
