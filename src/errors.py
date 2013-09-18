class MongolitoException(Exception):
    pass

class ParsingException(MongolitoException):
    def __init__(self, line, dn, message):
        self.line = line
        self.message = message
        self.dn = dn

    def __str__(self):
        return 'Error line %d "%s" : %s' % (self.line, self.dn, self.message)

class SkipObjectException(MongolitoException):
    '''This exception is used for flow control. If you raise it, it will
    stop processing the current object, for the current set of rules'''
    pass

class UnableToConnectException(MongolitoException):
    '''Raised when it is impossible to connect with a source. It should be raised
    if the very connection can't be establshed. If the source can be connected, 
    but something else occurs, throw a more specific error'''
    pass

class AuthenticationRequiredException(MongolitoException):
    '''Raised when connecting to a BaseGenerator object that requires authentication.
    Applications should handle this and provide a GUI allowing the user to enter a
    username and password.'''
    pass

class AuthenticationFailedException(MongolitoException):
    '''Raise when the supplied credentials are invalid.'''
    pass
