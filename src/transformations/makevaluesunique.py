from transformations import BaseTransformation

class MakeValuesUnique(BaseTransformation):
    def __init__(self, attribute):
        self.attribute = attribute

    def transform(self, original, ldapobject):
        """
        If the attribute is present, makes all values it 
        contains unique. Does not preserve order.
        """
        try:
            #save the new list without duplicates
            ldapobject[self.attribute] = list(set(ldapobject[self.attribute]))

        except KeyError:
            #The attribute does not exist
            pass

        return ldapobject

