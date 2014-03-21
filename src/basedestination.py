class BaseDestination(object):
    '''
    This is the base class for objects that receive a stream of ldapobjects
    to output.
    '''

    def start(self, username=None, password=None, name=None):
        self.connect()
        return self

    def stop(self):
        self.disconnect()
        return self

    def add(self, original, current, undo=False):
        pass

    def delete(self, original, current, undo=False):
        pass

    def comment(self, xxx):
        pass

    def modify(self, original, current, undo=False):
        pass


