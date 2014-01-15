import basegenerator
import logging



class Factory(object):
    '''
    This is the base class for objects that register a method 
    capable of creating a class from a given uri
    '''
    __borg_shared_state = {}
    __borg_shared_state['factories'] = []


    def __init__(self):
        #Monostate class, better than singleton
        self.__dict__ = self.__borg_shared_state


    def register(self, classobject, detection):
        '''Classes send a bound method or function that will accept
        a uri and possibly return an object capable of handling the 
        objects it holds.

        Arguments:
            name (string): the name of the created objet (will show in
                           the logs
            detection : a bound method or function that will analyse a
                        uri it is given and return an object capable 
                        of handling it, or None if it can't.
        '''
        is_input = issubclass(classobject, basegenerator.BaseGenerator)

        #Saves the name and creation routine
        self.factories.append({'name':classobject.__name__,'detection':detection, 'input':is_input})

        
    def create(self, params):
        '''This method will loop through the factories, in the order they
        were registered, and ask them for an object capable of handling 
        the uri they are presented with. 

        Arguments:
            params (dict) : a dictionary of attributes and values for this connection

        Return value:
            A handler for the input or None if it could not find a 
            suitable handler.
        '''
        from main import URI, TYPE, INPUT
        created = None
        try:
            uri = params['uri']
            is_input = params.get(TYPE, INPUT) == INPUT
            for producer in self.factories:
                #If the producer's type is the same as the type attribute
                #in the param dict
                if producer['input'] == is_input:
                    created = producer['detection'](uri)
                    if created:
                        logging.info('{} created for uri {}'.format(producer['name'], uri))
                        break
                    else:
                        logging.debug('{} could not handle uri {}'.format(producer['name'], uri))

            if created is None:
                logging.error('No suitable factory found to handle {} uri {}'.format('input' if is_input else 'output', uri))
        except KeyError:
            logging.error('No uri provided')

        return created


if __name__ == "__main__":
    def create_42(uri):
        return 42 if uri.startswith('42') else None

    def create_666(uri):
        return 666 if uri.startswith('666') else None
    
    factory = Factory()

    factory.register('creator of 42', create_42)
    factory.register('creator of 666', create_666)

    print factory.create('42')
    print factory.create('666')
    print factory.create('bad')

