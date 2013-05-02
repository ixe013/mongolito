import re

def add_value(original, toadd):
    '''Handles the switch from single to multi-value.
    Also deals with None as an original value'''
    result = None
    if original is None:
        #New value altogether
        result = toadd
    elif isinstance(original, list):
        if isinstance(toadd, list):
            #Adding a multi-value to another multi-value
            result = original+toadd
        else:
            #Adding a single value to a multi-value
            original.append(toadd)
            result = original
    else:
        if isinstance(toadd, list):
            #Adding a single value to a multi-value
            toadd.append(original)
            result = toadd
        else:
            #Adding a multi-value to another multi-value
            result = [original, toadd]
        
    return result
        
class BaseTransformation(object):
    def __call__(self, data):
        for ldapobject in data:
            yield self.transform(ldapobject)
