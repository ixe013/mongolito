from transformations import BaseTransformation

class JoinMultiValueAttribute(BaseTransformation):
    '''Joins all the values of a multi-value attribute into a string, with an
    optional separator.

    '''
    def __init__(self, attribute, separator=None, newname=None):
        '''
        >>>joiner = JoinMultiValueAttribute('owner', 'info')

        :attribute the name of the attribute whose value will be merged
        '''
        self.attribute = attribute
        self.separator = separator or ''
        if newname is None:
            self.newname = attribute
        else:
            self.newname = newname
 
    def transform(self, original, ldapobject):
            try:
                ldapobject[self.newname] = [self.separator.join(ldapobject[self.attribute])]
            except KeyError:
                pass
    
            return ldapobject
