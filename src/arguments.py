import argparse
import collections
import logging
import logging.handlers
import time

import insensitivedict

__all__ = ['Arguments']

LOG_FILENAME='mongolito.log'
LOG_FORMAT = '%(asctime)s;%(levelname)s;%(filename)s:%(lineno)d;%(message)s' #Make it csv like (except for the message part)
LOG_TIMEFORMAT = None #default is fine

class Arguments(object):
    '''Processes and stores the arguments received at the command line.

    This class is a monostate class, aka Borg class. Multiple instances
    share state.
    '''
    #The name to value is not available to outside
    #modules but we have everything to make it up
    _logging_levels = collections.OrderedDict([
        (logging.getLevelName(logging.CRITICAL), logging.CRITICAL),
        (logging.getLevelName(logging.ERROR), logging.ERROR),
        (logging.getLevelName(logging.WARNING),  logging.WARNING),
        (logging.getLevelName(logging.INFO),  logging.INFO),
        (logging.getLevelName(logging.DEBUG), logging.DEBUG),
    ])

    #From Alex Martelli : http://code.activestate.com/recipes/66531/
    __borg_shared_state = {}

    def __init__(self):
        #Monostate class, better than singleton
        self.__dict__ = self.__borg_shared_state
    
    def parse(self):
        '''
        Parses the command line arguments to build a dict of name(s) and uri(s)
        that will be ready to be instanciated.

        It also takes action on the following optional arguments, if present :
            trace : sets the logging level
        '''
        self._parser = argparse.ArgumentParser()
        self._parser.add_argument('-t', '--trace', choices=self._logging_levels.keys(), default=logging.getLevelName(logging.WARNING))

        args = self._parser.parse_known_args()

        root_logger = logging.getLogger()

        #Sets the logging level
        root_logger.setLevel(self._logging_levels[args[0].trace])

        formatter = logging.Formatter(LOG_FORMAT, LOG_TIMEFORMAT)

        rotating_handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, backupCount=5)
        rotating_handler.setFormatter(formatter)

        root_logger.addHandler(rotating_handler)

        #Each run starts a new log file
        rotating_handler.doRollover()

        logging.info('Mongolito started.')

        named_uris = args[-1:][0]

        self._connections =  insensitivedict.InsensitiveDict({})

        for connexion in named_uris:
            name, uri = connexion.split('=',1)

            if name in self._connections:
                logging.warning('Redefinition of URI %s from %s to %s', name, self._connections[name], uri)

            self._connections[name] = uri


    @property
    def connections(self):
        return self._connections


if __name__ == '__main__':
    args = Arguments()
    args.parse()

    connexions = args.connexions

    for name,uri in connexions.items():
        print name+'='+uri

