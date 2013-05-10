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

def compute_path(dn):
    '''Returns a string of all the components minus the first one.

    By convention, metadata is always lowercase.

    >>> compute_path('CN=someone,DC=example,DC=com')
    'dc=example,dc=com'
    >>> compute_path('DC=com')
    'dc=com'

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

def get_insensitive_key(d, key):
    '''Returns the key that is in the dict, ignoring
    case. Returns a KeyError if the key is not found.'''
    key = key.lower()
    
    result = None

    for k in d:
        if k.lower() == key:
            result = k
            break

    return result


def get_insensitive_value(d, key):
    return d[get_insensitive_key(d, key)]

