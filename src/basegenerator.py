import getpass
import sys

import errors

class BaseGenerator(object):
    '''
    This is the base class for objects that generate a stream of ldapobjects
    '''

    def get_attribute(self, query={}, attribute = 'dn', error=KeyError):
        '''
        Returns an iterator over a single attribute from a search.
        '''
        for ldapobject in self.search(query, [attribute]):
            try:
                yield ldapobject[attribute]
            except KeyError as ke:
                if error is not None:
                    raise ke

    def get_search_object(self, query={}, attributes=[]):
        '''
        Helper that returns a generator function
        '''
        return self.search(query, attributes)

    def start(self, name=''):
        '''Generic method that wraps connect and handles prompting the user 
        for a password if required.
        
        Arguments:
            name (string) : Used for prompts and logs only
        '''
        username = ''
        password = ''

        while(True):
            try:
                self.connect(username, password)
                break
            except errors.AuthenticationRequiredException:
                username = raw_input('Enter a username for input {} '.format(name))
                password = getpass.getpass('Password ')        
            except errors.AuthenticationFailedException:
                print >> sys.stderr, 'Authentication failed'
                username = raw_input('Enter a username for input {} '.format(name))
                password = getpass.getpass('Password ')        

    def stop(self):
        '''Generic method that wraps disconnect. Does nothing else for now
        but there for symetry with start'''
        self.disconnect()

    @property 
    def name(self):
        return self.name
