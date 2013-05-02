class RemoveAttribute(object):
    '''Removes an attribute, regardless of value.

    '''
    def __init__(self, attribute):
        '''
        >>>remover = RemoveAttribute('logintime')

        :attribute the name of the attribute from which a value must be removed
        '''
        self.attribute = attribute
 
    def __call__(self, data):
        '''
        :data a dictionary reprenting one entry
        '''
        #For each dictionary object to process
        for ldapobject in data:
            try:
                del ldapobject[self.attribute]
            except KeyError:
                pass

            #Return the object, possibly modified                
            yield ldapobject
 
