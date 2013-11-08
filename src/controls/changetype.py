import logging
import re

import utils

from transformations import BaseTransformation
import errors

class ChangeType(BaseTransformation):
    """Carries information about the type of change requested.

    """
    add='add'
    changetypes = [add]
    
    def __init__(self, change, attribute):
        """
        Informs processing what method to call on the output
        object.

        >>>changer = ChangeType(ChangeType.modify, 'member')

        Args:
            change (string): One of the supported change types
            attribute (string): the name of the attribute from which a value must be removed
        """
        self.change = change
        self.attribute = attribute
 
    def transform(self, original, ldapobject):
        """
        The transformation will mimic LDAP changetype mechanism by adding
        an operational attribute named 'changetype' and a list of attributes
        to change.

        Change type rules are as follow (in case there are many):
           - There can only be one changetype. The last one stays.
           - Multiple attributes can be added
        
        """
        ldapobject['changetype'] = self.change
        #The attributes to change 
        ldapobject.setdefault(self.change, []).append(self.attribute)
        #Return the object
        return ldapobject
 

