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
        for ldapobject in data:
            #Copy over to a new dict is easier
            transformed = {}
        
            #For each key value pair in the orginal dict
            for attribute,value in ldapobject.iteritems():
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
        self.pattern = re.compile(value.strip('/'), flags=re.IGNORECASE)
 
    def __call__(self, data):
        '''
        :data a dictionary reprenting one entry
        '''
        #For each dictionary object to process
        for ldapobject in data:
            #For each key value pair in the orginal dict
            for attribute,value in ldapobject.iteritems():
                if attribute == self.attribute:
                    #If the attribute is multi-valued
                    if isinstance(value, list): 
                        #Remove the value
                        new_value = filter(lambda v: not self.pattern.match(v), value)
                        #Make a single item list into that item
                        if len(new_value)==1:
                            ldapobject[attribute] = new_value[0]
                        #Delete the attribute if it was the last item
                        elif len(new_value)==0:
                            del ldapobject[attribute]
                        #Or save the remaining items from the list
                        else:
                            ldapobject[attribute] = new_value

                    #If the attribute is a string
                    elif isinstance(value, basestring):
                        if self.pattern.match(value):
                            del ldapobject[attribute]

                    #The attribute name is not a regex, so there can only be
                    #one match.
                    break

            #Return the object, possibly modified                
            yield ldapobject
 
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
        for ldapobject in data:
            try:
                del ldapobject[self.attribute]
            except KeyError:
                pass

            #Return the object, possibly modified                
            yield ldapobject
 
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
        self.pattern = re.compile(pattern.strip('/'), flags=re.IGNORECASE)
        self.replacement = replacement
 
    def __call__(self, data):
        '''
        :data a dictionary reprenting one entry
        '''
        #For each dictionary object to process
        for ldapobject in data:
            for attribute,value in ldapobject.iteritems():
                if attribute == self.attribute:
                    #If the attribute is multi-valued
                    if isinstance(value, list): 
                        ldapobject[attribute] = [re.sub(self.pattern, self.replacement, v) for v in value]
                    #If the attribute is a string
                    elif isinstance(value, basestring):
                        ldapobject[attribute] = re.sub(self.pattern, self.replacement, value)

                    #The attribute name is not a regex, so there can only be
                    #one match.
                    break

            #Return the object, possibly modified                
            yield ldapobject
 
class AddAttribute(object):
    '''Adds an attribute to an object.
    
    If the value is already present, it is added and the value 
    is turned into a list if it is not one already.

    We make sure the object is a string, so that method can be passed
    to it.

    '''
    def __init__(self, attribute, value):
        self.attribute = attribute
        self.value = value

    def __call__(self, data):
        '''
        :data a dictionary reprenting one entry
        '''
        #For each dictionary object to process
        for ldapobject in data:
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

            yield ldapobject
            
class MakeValuesUnique(object):
    def __init__(self, attribute):
        self.attribute = attribute

    def __call__(self, data): 
        '''Alex Martelli, order preserving. 
        Found at http://www.peterbe.com/plog/uniqifiers-benchmark

        '''
        for ldapobject in data:
            seen = {}
            result = []

            try:
                for item in ldapobject[self.attribute]:
                    marker = item
                    # in old Python versions:
                    # if seen.has_key(marker)
                    # but in new ones:
                    if marker in seen: continue
                    seen[marker] = 1
                    result.append(item)

                #Maybe we merged everything to a single item
                if len(result) == 1:
                    #If so, make it single valued
                    ldapobject[self.attribute] = result[0]
                else:
                    #save the new list
                    ldapobject[self.attribute] = result

            except KeyError:
                pass

            yield ldapobject

class CopyFirstValueOfAttribute(object):
    def __init__(self, fromattr, toattr):
        self.fromattr = fromattr
        self.toattr = toattr

    def __call__(self, data):
        '''Takes the first attribute from an attribute and
        copies it over to another attribute. Works with mutli-
        values on both source and destination'''
        for ldapobject in data:
            try:
                tocopy = None

                if isinstance(ldapobject[self.fromattr], list):
                    tocopy = ldapobject[self.fromattr][0]                    
                else:
                    tocopy = ldapobject[self.fromattr]                    
                    
                ldapobject[self.toattr] = add_value(ldapobject.get(self.toattr), tocopy)

            except KeyError:
                pass

            yield ldapobject
        
