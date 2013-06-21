import base64
import hashlib
import random
import string
import sys

class PasswordGenerator(str):
    '''Behaves like a string, but returns a different somewhat random value
    each time. 

    '''
    def __init__(self, length=13):
        self.length = length
        random.seed()

    def __str__(self):
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
            premaster = ''.join([chr(random.randint(0,255)) for x in xrange(0,self.length)])
            #Base64 to get a large number of printable chars, adding special chars
            #which are missing from the base64 encoding
            master = base64.b64encode(premaster)+special
            #Shuffle those characters around and return a password
            #That is as long as required
            password = ''.join(random.sample(master,len(master)))[0:self.length]

            #Honest attemp to pass most password policy requirements
            if (set(password) & set(special) and
                set(password) & set(string.lowercase) and
                set(password) & set(string.uppercase) and
                set(password) & set(string.digits)):
                #If we get here, we have our password
                break

        return password

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
        #We've hit the last pert of the key, return that
        #Might raise a KeyError, just a like a dict.
        return ldapobject[attribute]
    
