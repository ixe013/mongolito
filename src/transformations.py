
class RenameAttribute(object):
    '''Takes a key name and renames it, keeping values intact.

    Uses Python's re.sub(), so fancy renames with expression
    groups can be used.
    '''
 
    def __init__(self, pattern, replacement):
        '''
        >>>renamger = RenameAttribute('(.*)bar', r'blah\1')

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
 
