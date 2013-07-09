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
