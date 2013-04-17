import textwrap
import base64
import string


RFC2849_MAX_LINE = 76

def RFC2849WrappedOuput(attribute, separator, value):
    '''Wraps the value in a RFC2849 compliant manner.
    Returns a array of lines to print.'''
    wrapper = textwrap.TextWrapper()

    #Wrap length is the maximum line length, minus the leading space
    wrapper.width=RFC2849_MAX_LINE-1

    #The initial whitespace will be replaced by the attribute name
    #and ::, the encoded line separator, later on in this method
    wrapper.initial_indent=' '*(len(attribute)+len(separator))

    #Other lines begin with a single space
    wrapper.subsequent_indent=' '

    #Wrap the whole thing
    result = wrapper.wrap(base64.b64encode(value))

    #Remove the leading blank space with the attribute name
    result[0] = attribute + separator + result[0].strip()
        
    return result
    

def makePrintableAttributeAndValue(attribute, value):
    separator = ':'

    #If line ends with a space, we must base64 it.
    if value[-1:] == ' ':
        separator = separator*2
        value = base64.b64encode(value)

    #Else if is has anything other than plain old ascii characters
    #(binary values like jpeg or certificates fall under this)
    elif all(ord(c) >= ord(' ') and ord(c) < 127 and c in string.printable for c in value):
        separator = separator*2
        value = base64.b64encode(value)
            

    #Is line does too long to fit on a RFC2849 line of 76 chars ?
    return RFC2849WrappedOuput(attribute, separator+' ', value)


def printAttributeAndValue(printable):
    print '\n'.join(printable)


def printDictAsLDIF(ldapObject):
    '''Prints a Python dict that represents a ldap object in a sorted matter
         dn is printed first
         objectclass is printed after, sorted
         remaining attributes are printed after, sorted by key name.
         multiple values for an attribute are also sorted.
       Hence any valid unsorted ldif will comme out the same way from this 
       method'''

    #dn is always first
    #print 'dn:', ldapObject['dn']
    printAttributeAndValue(makePrintableAttributeAndValue('dn',ldapObject['dn']))

    #Remove the attributes we already printed
    del ldapObject['dn']
    
    #Now with the object classes
    try:
        for objclass in sorted(ldapObject['objectclass']):
            printAttributeAndValue(makePrintableAttributeAndValue('objectclass',objclass))
        del ldapObject['objectclass']

    except KeyError:
        #object class is not mandatory
        pass

    #This loops prints what is left
    for name in sorted(ldapObject.keys()):
        #Must check type instead of begging for forgiveness
        #because string is iterable but will not produce the
        #output we are looking for
        if type(ldapObject[name]) in [type(''), type(u'')]:
            printAttributeAndValue(makePrintableAttributeAndValue(name,ldapObject[name]))
        else:
            #Print values prefixed with attribute name, sorted
            for value in sorted(ldapObject[name]):
                printAttributeAndValue(makePrintableAttributeAndValue(name,value))

    #Ends with an empty line
    print
            

def createPrintOutput(args):
    'Trivial polymorphic helper'
    return printDictAsLDIF


