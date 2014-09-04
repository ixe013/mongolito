from transformations import BaseTransformation

class CopyFirstValueOfAttribute(BaseTransformation):
    def __init__(self, fromattr, toattr):
        self.fromattr = fromattr
        self.toattr = toattr

    def transform(self, original, ldapobject):
        """
        Takes the first attribute from an attribute and
        copies it over to another attribute. Works with mutli-
        values on both source and destination
        """
        try:
            ldapobject.setdefault(self.toattr, []).extend(ldapobject[self.fromattr])
        except KeyError:
            #fromattr is absent
            pass

        return ldapobject
        
