from transformations import BaseTransformation

class MakeValuesUnique(BaseTransformation):
    def __init__(self, attribute):
        self.attribute = attribute

    def transform(self, original, ldapobject):
        """
        If the attribute is present, makes all values it 
        contains unique. Does not preserve order.
        """
        seen = set()

        try:
            for item in ldapobject[self.attribute]:
                if item not in seen: 
                    seen.add(item)

            #save the new list
            ldapobject[self.attribute] = list(seen)

        except KeyError:
            #The attribute does not exist
            pass

        return ldapobject

