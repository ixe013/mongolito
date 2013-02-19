
class LDIFParsingException(Exception):
    def __init__(self, line, message):
        self.line = line
        self.message = message

    def __str__(self):
        return 'Error line %d: %s' % (line, message)


