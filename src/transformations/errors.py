
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
    pass
