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

    def start(self, username=None, password=None, name=None):
        '''Generic method that wraps connect and handles prompting the user 
        for a password if required.
        
        Arguments:
            name (string) : Used for prompts and logs only

        Returns self
        '''
        _username = username or ''
        _password = password or ''
        _name = name or self.name

        for i in range(0,3):
            try:
                self.connect(_username, _password)
                break
            except errors.AuthenticationRequiredException:
                _username = raw_input('Enter a username for {} [{}] '.format(_name, _username)) or _username
                _password = getpass.getpass('Password ')        
            except errors.AuthenticationFailedException:
                print >> sys.stderr, 'Authentication failed'
                _username = raw_input('Enter a username for {} [{}] '.format(_name, _username)) or _username
                _password = getpass.getpass('Password ')        

        return self

    def stop(self):
        '''Generic method that wraps disconnect. Does nothing else for now
        but there for symetry with start'''
        self.disconnect()
        return self

    @property 
    def name(self):
        return self._name
