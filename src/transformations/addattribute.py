from transformations import BaseTransformation

class AddAttribute(BaseTransformation):
    '''Adds an attribute to an object.

    If the value is already present, it is added and the value
    is turned into a list if it is not one already.

    We make sure the object is a string, so that method can be passed
    to it.

    '''
    def __init__(self, attribute, value):
        self.attribute = attribute
        self.value = value

    def transform(self, ldapobject):
        '''
        :data a dictionary reprenting one entry
        '''
        try:
            #Do we have a multi-value attribute ?
            if isinstance(ldapobject[self.attribute], list):
                ldapobject[self.attribute].append(str(self.value))
            #else we have a single-value that becomes multi-valued
            else:
                ldapobject[self.attribute] = [ldapobject[self.attribute], str(self.value)]
        except KeyError:
            #We dit not have that value, add it
            ldapobject[self.attribute] = str(self.value)

        return ldapobject
