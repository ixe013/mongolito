class BaseDestination(object):
    '''
    This is the base class for objects that receive a stream of ldapobjects
    to output.
    '''

    def start(self, name=''):
        self.connect()

    def stop(self):
        self.disconnect()

