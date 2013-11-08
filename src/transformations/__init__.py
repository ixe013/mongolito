import re

        
class BaseTransformation(object):
    def __call__(self, data):
        for ldapobject in data:
            yield self.transform(ldapobject)

    def transform(self, original, modified):
        pass
