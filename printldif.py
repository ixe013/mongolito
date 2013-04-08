import textwrap
import base64

def RFC2849WrappedOuput(attribute, value):
    '''Wraps the value in a RFC2849 compliant manner.
    Returns a array of lines to print. If the value can 
    be printed as-is, a single item array is returned'''
    MAX_LINE = 76
    line_separator = ': '

    #Sensible default
    result = [attribute + line_separator + value]

    if len(attribute) + len(value) + len(line_separator) > MAX_LINE:
        encoded_line_separator = ':: '
        wrapper = textwrap.TextWrapper()

        #Wrap length is the maximum line length, minus the leading space
        wrapper.width=MAX_LINE-1

        #The initial whitespace will be replaced by the attribute name
        #and ::, the encoded line separator.
        wrapper.initial_indent=' '*(len(attribute)+len(encoded_line_separator))

        #Other lines begin with a single space
        wrapper.subsequent_indent=' '

        #Wrap the whole thing
        result = wrapper.wrap(base64.b64encode(value))

        #Remove the leading blank space with the attribute name
        result[0] = attribute + encoded_line_separator + result[0].strip()
        
    return result
    

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
        if type(ldapObject[name]) in [type(''), type(u'')]:
            #Single value
            print name+u':',ldapObject[name].encode('utf-8')
        else:
            #Print values sorted
            for value in sorted(ldapObject[name]):
                print name+u':',value.encode('utf-8')

    #Ends with an empty line
    print
            


def createPrintOutput(args):
    'Trivial polymorphic helper'
    return printDictAsLDIF


if __name__ == '__main__':
    for l in RFC2849WrappedOuput('dn', 'Bonjour a tous mes amis de la Guadeloupe'*10):
        print l
