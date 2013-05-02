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
 
    def transform(self, ldapobject):
        '''
        :data a dictionary reprenting one entry
        '''
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
        return ldapobject
 
