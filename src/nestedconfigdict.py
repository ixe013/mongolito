import collections

_default_dict=collections.OrderedDict


def get_top_level_config_elements(configuration, dict_type=_default_dict, section=None):
    '''Takes a configuration object and converts key that have dots
    as top level keys in a nested dict object.

    Example :
        [Section1]
        server=example.com
        server.www=web.example.com
        server.ftp=files.example.com
        location=Building1
        localtion.room=1234
        waranty=expired

    Will produce :
       { 'server':'example.com',
         'location':'Building1',
         'waranty':'expired'
       }

    >>> config.set('Section1', 'server', 'example.com')
    >>> config.set('Section1', 'server.www', 'web.example.com')
    >>> config.set('Section1', 'server.ftp', 'files.example.com')
    >>> config.set('Section1', 'location', 'Building1')
    >>> config.set('Section1', 'location.room', '1234')
    >>> config.set('Section1', 'waranty', 'expired')
    >>> get_top_level_config_elements(config, 'Section1')
    OrderedDict([('server', 'example.com'), ('location', 'Building1'), ('waranty', 'expired')])

    Arguments :
        configuration (ConfigParser) : a loaded configuration object
        dict_type (type) : the dict type to use. Defaults to colllections.OrderedDict
    '''
    result = dict_type()

    try:
        _section = section or configuration.sections()[0]

        #Get the 'top level' keys
        result = dict_type([(k,v) for k,v in configuration.items(_section) if '.' not in k])

    finally:
        return result

def get_nested_config_elements(configuration, parent, dict_type=_default_dict, section=None):
    '''Takes a configuration dictionary and converts key that have dots
    as top level keys in a nested dict object.

    Example :
        [Section1]
        server=example.com
        server.www=web.example.com
        server.www.owner=marketing
        server.ftp=files.example.com
        location=Building1
        localtion.room=1234
        waranty=expired

    When called with 'server' as the parent key will produce :
       { 'www':'www.example.com',
         'ftp':'ftp.example.com'
       }

    Arguments :
        configdict (ConfigParser) : a loaded configuration dict
        parent (string) : the name of the prefix. Can be nested itself, like 'server.www'
        dict_type (type) : the dict type to use. Defaults to colllections.OrderedDict
    '''
    result = dict_type()

    try:
        #Use the first section as a default
        _section = section or configuration.sections()[0]

        #For each top level key          
        for key,value in configuration.items(_section):
            try:
                #If the key that starts with the parent key name and a dot
                if key.index(parent+'.') == 0:
                    child = key[len(parent)+1:]
                    result[child] = value
            except ValueError:
                #key not found, carry on
                pass
    finally:
        return result


if __name__ == '__main__':
    import ConfigParser
    import insensitivedict
    from pprint import pprint as pp

    config = ConfigParser.SafeConfigParser()

    config.add_section('Section1')
    config.set('Section1', 'server', 'example.com')
    config.set('Section1', 'server.www', 'web.example.com')
    config.set('Section1', 'server.ftp', 'files.example.com')
    config.set('Section1', 'location', 'Building1')
    config.set('Section1', 'location.room', '1234')
    config.set('Section1', 'waranty', 'expired')
    config.set('Section1', 'input', '@server')

    top = get_top_level_config_elements(config, insensitivedict.InsensitiveDict, 'Section1')
    pp(top)

    nested = get_nested_config_elements(config, 'input')
    pp(nested)

