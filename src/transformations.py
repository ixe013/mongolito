import re

class RenameAttribute(object):
    '''Takes a key name and renames it, keeping values intact.

    Uses Python's re.sub(), so fancy renames with expression
    groups can be used.
    '''
 
    def __init__(self, pattern, replacement):
        '''
        >>>renamer = RenameAttribute('(.*)bar', r'blah\1')

        :pattern A valid PCRE pattern
        :replacement A string (than can refer to the pattern with expression groups)
        '''
        self.pattern = re.compile(pattern)
        self.replacement = replacement
 
    def __call__(self, data):
        '''
        :data a dictionary reprenting one entry
        '''
        #For each dictionary object to process
        for ldapObject in data:
            #Copy over to a new dict is easier
            transformed = {}
        
            #For each key value pair in the orginal dict
            for attribute,value in ldapObject.iteritems():
                #Save a transformed key value pair.
                #Values (even complex ones) are untouched
                #re.sub will not change attribute names that don't match
                #Does not check if a key with the same name already 
                #exists or try to merge with it
                transformed[re.sub(self.pattern, self.replacement, attribute)] = value

            #Return the new object                
            yield transformed
 
class RemoveValue(object):
    '''Removes a value from an attribute, possibly deleting it.

    If the value is the last one for the attribute, the attribute 
    is deleted. When removing from a list, if there is a single attribute 
    left after the operation, it keeps only the object, (value = value[0])

    '''
    def __init__(self, attribute, value):
        '''
        >>>remover = RemoveValue('objectClass', 'irrelevant')

        :attribute the name of the attribute from which a value must be removed
        :value the value to be removed. Can be a regular expression enclosed in //
        '''
        self.attribute = attribute
        self.pattern = re.compile(value.strip('/'))
 
    def __call__(self, data):
        '''
        :data a dictionary reprenting one entry
        '''
        #For each dictionary object to process
        for ldapObject in data:
            #For each key value pair in the orginal dict
            for attribute,value in ldapObject.iteritems():
                if attribute == self.attribute:
                    #If the attribute is multi-valued
                    if isinstance(value,list): 
                        #Remove the value
                        new_value = filter(lambda v: not self.pattern.match(v), value)
                        #Make a single item list into that item
                        if len(new_value)==1:
                            ldapObject[attribute] = new_value[0]
                        #Delete the attribute if it was the last item
                        elif len(new_value)==0:
                            del ldapObject[attribute]
                        #Or save the remaining items from the list
                        else:
                            ldapObject[attribute] = new_value

                    #If the attribute is a string
                    elif isinstance(value,basestring):
                        if self.pattern.match(value):
                            del ldapObject[attribute]

                    #The attribute name is not a regex, so there can only be
                    #one match.
                    break

            #Return the object, possibly modified                
            yield ldapObject
 
class RemoveAttribute(object):
    '''Removes an attribute, regardless of value.

    '''
    def __init__(self, attribute):
        '''
        >>>remover = RemoveAttribute('logintime')

        :attribute the name of the attribute from which a value must be removed
        '''
        self.attribute = attribute
 
    def __call__(self, data):
        '''
        :data a dictionary reprenting one entry
        '''
        #For each dictionary object to process
        for ldapObject in data:
            try:
                del ldapObject[attribute]
            except KeyError:
                pass

            #Return the object, possibly modified                
            yield ldapObject
 
class RenameValue(object):
    '''Renames a value with a regular expression pattern.

    Each value in multi-valued attributes are tested for 
    a match and renamed if necessary.

    '''
    def __init__(self, attribute, pattern, replacement):
        '''
        >>>renamer = RenameValue('dn', '/.*ou=AAA.*/', r'\1ou=BBB\2')

        :attribute the name of the attribute from which a value must be removed
        '''
        self.attribute = attribute
        self.pattern = pattern
        self.replacement = replacement
 
    def __call__(self, data):
        '''
        :data a dictionary reprenting one entry
        '''
        #For each dictionary object to process
        for ldapObject in data:
            for attribute,value in ldapObject.iteritems():
                if attribute == self.attribute:
                    #If the attribute is multi-valued
                    if isinstance(value,list): 
                        ldapObject[attribute] = [re.sub(self.pattern, self.replacement, v) for v in value]
                    #If the attribute is a string
                    elif isinstance(value,basestring):
                        ldapObject[attribute] = re.sub(self.pattern, self.replacement, value)

                    #The attribute name is not a regex, so there can only be
                    #one match.
                    break

            #Return the object, possibly modified                
            yield ldapObject
 
