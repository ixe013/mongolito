from transformations import BaseTransformation

class CopyAttribute(BaseTransformation):
    def __init__(self, original, copy):
        self.original = original
        self.copy = copy

    def transform(self, original, ldapobject):
        '''Copies an attribute to another one, leaving the original 
        intact, unlike RenameAttribute. If the destination attribute
        exists, it will be overwritten.

        '''
        try:
            ldapobject[self.copy] = ldapobject[self.original]

        except KeyError:
            pass

        return ldapobject
        
