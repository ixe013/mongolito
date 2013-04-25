import random
import hashlib

class PasswordGenerator(str):
    '''Behaves like a string, but returns a different somewhat random value
    each time'''
    def __init__(self):
        random.seed()

    def __str__(self):
        '''Quick random password generator with good entropy. 

        Makes better passwords than any human can remember.

        '''
        premaster = hashlib.sha1(str(random.random())).hexdigest()+'!@#$%^&*()'
        return ''.join(random.sample(premaster,len(premaster)))

