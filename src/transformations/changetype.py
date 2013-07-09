from transformations import BaseTransformation

class ChangeType(BaseTransformation):
    '''Changes the default action to a change.
    '''
 
    def __init__(self, change, operation, attribute):
        self.change = change
        self.operation = operation
        self.attribute = attribute
 
    def transform(self, original, ldapobject):
        '''
        Adds attributes for replace
        '''
        ldapobject['changetype'] = self.change
        ldapobject[self.operation] = self.attribute

        return ldapobject
 
