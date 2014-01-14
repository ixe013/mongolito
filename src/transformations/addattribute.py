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

    def transform(self, original, ldapobject):
        '''
        :data a dictionary reprenting one entry
        '''
        try:
            ldapobject[self.attribute].append(str(self.value))
        except KeyError:
            #This is a new attribute for that object
            if isinstance(self.value, basestring):
                ldapobject[self.attribute] = [str(self.value)]
            else:
                ldapobject[self.attribute] = [str(x) for x in self.value]

        return ldapobject
