#!/usr/bin/python
'''Miscellaneous helper functions to help identifying the directory
'''
import ldap

def get_ldap_base(ldap_connection, timeout=-1):
    '''
    Returns the base DN from that ldap connection by inspecting the rootDSE.
    If the defaultNamingContext entry is present, it is returned. If not, the first
    naming context is used.
    
    The ldap_connection does not need to be bound (using simple_bind_s and such),
    as the rootDSE can be returned on an anonymous connection.

    Args:
        ldap_connection (ldap.LDAPObject): a connection to a LDAP directory, usually anynonymous. 
        timeout (int): The number of seconds to wait for the server to respond

    Returns:
        The DN of naming context found in that directory. It can be an empty string 
        and still be valid. 

        For more information on rootDSE, see RFC 2252.

    Raises:
        ldap.LDAPError: An error occured at the LDAP level (unreachable, etc.)
    '''
    basedn = ''

    ldap_result_id = l.search_st('', ldap.SCOPE_BASE, 'objectClass=*', ['namingContexts','defaultNamingContext'], timeout=timeout)

    result_type, result_data = l.result(ldap_result_id, 0)

    if result_type == ldap.RES_SEARCH_ENTRY:
        try:
            result = result_data[0][1]
            basedn = result['defaultNamingContext'][0]
        except KeyError:
            #No default naming context, we use the first 
            #naming context we found (or default to an 
            #empty string)
            naming_contexts = result.get('namingContexts',[''])
            basedn = naming_contexts[0]
        except IndexError:
            #No context were found. The default empty
            #string will be returned
            pass

    return basedn



if __name__ == '__main__':
    import sys
    try:
        l = ldap.open(sys.argv[1])
        print get_ldap_base(l)
    
    except IndexError:
        print >> sys.stderr, 'Pass the host name or IP'
    
