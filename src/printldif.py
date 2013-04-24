import argparse
import base64
import string


RFC2849_MAX_LINE = 76

def RFC2849WrappedOuput(line):
    '''Slices the attribute-value pair (which might be base64
    encoded at this point) into lines of at most 76 characters,
    with each wrapped line begining with a single space.

    Returns a array of lines to print.'''
    #TODO: 
    return [line]

def makePrintableAttributeAndValue(attribute, value):
    separator = ':'

    value = value.encode('utf-8')

    #If line ends with a space, we must base64 it.
    if value.endswith(' '):
        separator = separator*2
        value = base64.b64encode(value)

    #Else if is has anything other than plain old ascii characters
    #(binary values like jpeg or certificates fall under this)
    elif not all(ord(c) >= ord(' ') and ord(c) < 127 for c in value):
        separator = separator*2
        value = base64.b64encode(value)
            
    return attribute+separator+' '+value

        
class LDIFPrinter(object):
    def __init__(self, ldiffile):
        self.ldiffile = ldiffile
        
    @staticmethod
    def addArguments(parser):
        group = parser.add_argument_group('Writes objects in LDIF format')
        group.add_argument("-l",
                          "--ldif", dest="ldiffile",
                          type=argparse.FileType('w'),
                          help="The LDIF file to write. Use - for stdout")

        return parser

    @staticmethod
    def create(args):
        return LDIFPrinter(args.ldiffile)


    def printAttributeAndValue(self, printable):
        print >> self.ldiffile, '\n'.join(RFC2849WrappedOuput(printable))


    def write(self, ldapObject):
        '''Prints a Python dict that represents a ldap object in a sorted matter
             dn is printed first
             objectclass is printed after, sorted
             remaining attributes are printed after, sorted by key name.
             multiple values for an attribute are also sorted.
           Hence any valid unsorted ldif will comme out the same way from this 
           method'''

        #dn is always first
        #print 'dn:', ldapObject['dn']
        self.printAttributeAndValue(makePrintableAttributeAndValue('dn',ldapObject['dn']))

        #Remove the attributes we already printed
        del ldapObject['dn']
        
        try:
            self.printAttributeAndValue(makePrintableAttributeAndValue('changetype',ldapObject['changetype']))
            del ldapObject['changetype']
            
        except KeyError:
            pass
        #Now with the object classes
        try:
            for objclass in sorted(ldapObject['objectclass']):
                self.printAttributeAndValue(makePrintableAttributeAndValue('objectclass',objclass))
            del ldapObject['objectclass']

        except KeyError:
            #object class is not mandatory
            pass

        #This loops prints what is left
        for name in sorted(ldapObject.keys()):
            #Must check type instead of begging for forgiveness
            #because string is iterable but will not produce the
            #output we are looking for
            if isinstance(ldapObject[name], basestring):
                self.printAttributeAndValue(makePrintableAttributeAndValue(name,ldapObject[name]))
            else:
                #Print values prefixed with attribute name, sorted
                for value in sorted(ldapObject[name]):
                    self.printAttributeAndValue(makePrintableAttributeAndValue(name,value))

        #Ends with an empty line
        print
                
