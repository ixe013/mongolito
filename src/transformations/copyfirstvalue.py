from transformations import add_value
from transformations import BaseTransformation

class CopyFirstValueOfAttribute(BaseTransformation):
    def __init__(self, fromattr, toattr):
        self.fromattr = fromattr
        self.toattr = toattr

    def transform(self, ldapobject):
        '''Takes the first attribute from an attribute and
        copies it over to another attribute. Works with mutli-
        values on both source and destination'''
        try:
            tocopy = None

            if isinstance(ldapobject[self.fromattr], list):
                tocopy = ldapobject[self.fromattr][0]                    
            else:
                tocopy = ldapobject[self.fromattr]                    
                
            ldapobject[self.toattr] = add_value(ldapobject.get(self.toattr), tocopy)

        except KeyError:
            pass

        return ldapobject
        
