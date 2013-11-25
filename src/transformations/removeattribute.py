from transformations import BaseTransformation

class RemoveAttribute(BaseTransformation):
    '''Removes an attribute, regardless of value.

    '''
    def __init__(self, attribute):
        '''
        >>>remover = RemoveAttribute('logintime')

        :attribute the name of the attribute from which a value must be removed
        '''
        self.attribute = attribute
 
    def transform(self, original, ldapobject):
            try:
                #FIXME : would be nice to have a regex here, but we loose the index
                del ldapobject[self.attribute]
            except KeyError:
                pass
    
            return ldapobject
