def printDictAsLDIF(ldapObject):
    '''Prints a Python dict that represents a ldap object in a sorted matter
         dn is printed first
         objectclass is printed after, sorted
         remaining attributes are printed after, sorted by key name.
         multiple values for an attribute are also sorted.
       Hence any valid unsorted ldif will comme out the same way from this 
       method'''

    print 'dn:', ldapObject['dn']
    #Remove the attributes we already printed
    del ldapObject['dn']
    
    try:
        for objclass in sorted(ldapObject['objectclass']):
            print 'objectclass:',objclass
        del ldapObject['objectclass']

    except KeyError:
        #object class is not mandatory
        pass

    #This loops prints what is left
    for name in sorted(ldapObject.keys()):
        #Must check type, because string is iterable
        if type(ldapObject[name]) == type(''):
            #Single value
            print name+':',ldapObject[name]
        else:
            #Print values sorted
            for value in sorted(ldapObject[name]):
                print name+':',value

    #Ends with an empty line
    print
            
