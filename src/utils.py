import base64
import random
import string

def randomPassword(length):
    '''Quick random password generator with good entropy. 

    Makes better passwords than any human can remember.

    >>> generator = utils.PasswordGenerator()
    >>> len(str(generator))
    13
    >>> str(generator)
    ')G9FKM1=*s=&G'
    >>> str(generator)
    '&jnz8)@mjzO#$'
    >>> str(generator)
    'LN=82)E%FA&k('
    >>> str(generator)
    '^=l@G$3AQ#=vC'
    >>> str(generator)
    '@Vgd*1#)%5Vs('
    >>> str(generator)
    '1I$Lh)!lV^J41'
    '''
    special = '!@#$%^&*()'   
    password = ''                                   

    while True:
        #Generate N random numbers
        premaster = ''.join([chr(random.randint(0,255)) for _ in xrange(0,length)])
        #Base64 to get a large number of printable chars, adding special chars
        #which are missing from the base64 encoding
        master = base64.b64encode(premaster)+special
        #Shuffle those characters around and return a password
        #That is as long as required
        password = ''.join(random.sample(master,len(master)))[0:length]

        #Honest attemp to pass most password policy requirements
        if (set(password) & set(special) and
            set(password) & set(string.lowercase) and
            set(password) & set(string.uppercase) and
            set(password) & set(string.digits)):
            #If we get here, we have our password
            break

    return password

        
def makeUnicodePwd(pwd):
    '''Example taken from http://support.microsoft.com/kb/263991
    This function adds quotes and converts the password to the 
    format that ActiveDirectory expects.

    >>> pwd = u'"newPassword"'
    >>> base64.b64encode(pwd.encode('utf-16')[2:])
    'IgBuAGUAdwBQAGEAcwBzAHcAbwByAGQAIgA='
    >>> base64.b64encode(makeUnicodePwd('newPassword'))
    'IgBuAGUAdwBQAGEAcwBzAHcAbwByAGQAIgA='
    >>> base64.b64encode(makeUnicodePwd(u'newPassword'))
    'IgBuAGUAdwBQAGEAcwBzAHcAbwByAGQAIgA='
    '''      
    #Must be surrounded by quotes, for some reason
    pwd = '"'+pwd+'"'

    #Regular strings are ok. 
    if isinstance(pwd, str):
        #We just make them Unicode
        pwd = pwd.decode('utf-8')

    #base64 is done by the caller. Usually base64.b64encode will 
    #be called, but it could also be encoded in asn.1 or something
    return pwd.encode('utf-16')[2:]

class RandomPasswordGenerator(str):
    '''Behaves like a string, but returns a different somewhat random value
    each time.

    '''
    def __init__(self, length=13):
        self.length = length
        random.seed()
 
    def __str__(self):
        return randomPassword(self.length)
    
class RandomUnicodePasswordGenerator(str):
    '''Behaves like a string, but returns a different somewhat random value
    each time.
    '''
    def __init__(self, length=13):
        self.length = length
        random.seed()
 
    def __str__(self):
        return makeUnicodePwd(randomPassword(self.length))


def reverse_path(path):
    '''Returns a string of all the components in reverse order

    Whatever the order, applying this fonction twice has no effect

    >>> reverse_path('CN=someone,DC=example,DC=com')
    'dc=com,dc=example,cn=someone'
    >>> reverse_path('DC=com')
    'dc=com'

    '''
    components = path.split(',')
    components.reverse()
    #The parent is the joined path, minus the object 
    #itself (which is now last in the list)
    return ','.join(components).lower()


def compute_path(dn):
    '''Returns a string of all the components minus the first one.

    By convention, metadata is always lowercase.

    >>> compute_path('CN=someone,DC=example,DC=com')
    'dc=example,dc=com'
    >>> compute_path('DC=com')
    ''

    '''
    components = dn.split(',')
    #The parent is the joined path, minus the object 
    #itself (which is now last in the list)
    return ','.join(components[1:]).lower()

def compute_parent(dn):
    '''Returns a string of all the components reversed (minus the first one).

    By convention, metadata is always lowercase.

    >>> compute_parent('CN=someone,DC=example,DC=com')
    'dc=com,dc=example'
    >>> compute_parent('DC=com')
    ''

    '''
    components = dn.split(',')
    components.reverse()
    #The parent is the joined path, minus the object 
    #itself (which is now last in the list)
    return ','.join(components[:-1]).lower()

def extractRDN(dn):
    return dn.split(',',1)[0].split('=')[1]

def add_metadata(ldapobject, dn):
    ldapobject['mongolito'] = { 'parent':compute_parent(dn),
                                'path':compute_path(dn),
                              }

    #the RDN metadata is the value of the leftmost component. 
    #For example, an object with this dn 
    #  cn=USER,ou=people,dc=example,dc=com will
    #mongolito.rdn will be 'user'
    ldapobject['mongolito']['rdn'] = extractRDN(dn).lower()

    #for nesting calls
    return ldapobject


def regex_from_javascript(pattern, insensitive=True):
    '''Converts a javascript style regular expression to a 
    mongo regular expression suitable for in place replacement.

    Defaults to case insensitive. The trailing i is ignored, use
    the insensitive parameter.

    '''
    regex = {}
    regex['$regex'] = pattern_from_javascript(pattern)

    if insensitive:
        regex['$options'] = 'i'
    
    return regex

def simple_pattern_from_javascript(pattern):
    '''Converts a javascript style regular expression to a 
    glob-like pattern suitable for LDAP an most filesystems

    Defaults to case insensitive. The trailing i is ignored, use
    the insensitive parameter.

    '''
    
    _pattern = pattern_from_javascript(pattern)

    if not _pattern == pattern:
        #The pattern we received was indeed a javascript pattern
        #Let's take care of it
        if _pattern.startswith('^'): 
            #Remove the first character to make it
            #anchored to the line's begining
            _pattern = _pattern[1:]
        else:
            #Replace the first character with a *
            #because we are not anchored to the line's
            #begining
            _pattern = '*'+_pattern

        if pattern.endswith('$'):
            #Remove the last character will make it
            #anchored to the line's end.
            _pattern = _pattern[:-1]
        else:
            #Make the last character with a star
            #because we are not anchored to the line's 
            #end
            _pattern = _pattern+'*'
    else:
        #We received a plain string, we simply return it
        pass

    return _pattern
    
def pattern_from_javascript(pattern):
    '''Converts a javascript style regular expression to a 
    mongo regular expression suitable for in place replacement.

    Defaults to case insensitive. The trailing i is ignored, use
    the insensitive parameter.

    '''
    
    if pattern.startswith('/'): 
        if pattern.endswith('/'):
            pattern = pattern[1:-1]
        elif pattern.endswith('/i'):
            pattern = pattern[1:-2]

    return pattern
    
def get_nested_attribute(ldapobject, attribute):
    '''Returns an attribute with code that is metadata aware.

    get_attribute('mongolito.rdn',ldapobject) will become
    ldapobject['mongolito']['rdn']

    returns a KeyError if any key is missing (either mongolito
    or rdn, in this example).

    For regular keys, defaults to ldapboject[attribute]

    '''
    try:
        #Get the first member
        key, remaining_keys = attribute.split('.',1)
        return get_nested_attribute(ldapobject[key], remaining_keys)
    except ValueError:
        #We've hit the last part of the key, return that
        #Might raise a KeyError, just a like a dict.
        #The ValueError means that we were not able to unpack
        #the attribute (there are no dots left in it, or there were
        #no dots to begin with)
        return ldapobject[attribute]
    
