
class FromTemplate(object):

    def __init__(self, template, howmany):
        '''Returns the template object so many times'''
        self.template = template
        self.howmany = howmany

    @staticmethod
    def addArguments(parser):
        return parser

    @staticmethod
    def create_from_uri(name, uri):
        '''Not implemented, returns None'''
        return None

    def search(self, query = {}, attributes=[]):
        '''Thin wrapper over pymongo.collection.find'''

        for i in xrange(0, self.howmany):
            yield self.template

