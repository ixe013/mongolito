import argparse
import base64
import string


RFC2849_MAX_LINE = 76
CHUNK_MAX_VALUES = 1337

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
    #And me make a special case with the password (obscurity)
    elif 'userpassword' == attribute.lower():
        separator = separator*2
        value = base64.b64encode(value)
            
    return attribute+separator+' '+value

        
class LDIFPrinter(object):
    def __init__(self, ldiffile, overwrite):
        self.ldiffile = ldiffile

        if overwrite:
            self.ldiffile.truncate(0)
        
        
    @staticmethod
    def addArguments(parser):
        group = parser.add_argument_group('Writes objects in LDIF format')
        group.add_argument("-l",
                          "--ldif", dest="ldiffile",
                          type=argparse.FileType('a'),
                          help="The LDIF file to write to (append mode, unless --overwrite is specified). Use - for stdout")

        group.add_argument("-w",
                          "--overwrite", dest="overwrite",
                          action='store_true',
                          help="Will overwrite the destination if it exists")

        return parser

    @staticmethod
    def create(args):
        return LDIFPrinter(args.ldiffile, args.overwrite)


    def comment(self, text):
        print >> self.ldiffile, '#', text

    def printAttributeAndValue(self, printable):
        print >> self.ldiffile, '\n'.join(RFC2849WrappedOuput(printable))

    def write(self, ldapobject):
        '''Prints a Python dict that represents a ldap object in a sorted matter
             dn is printed first
             objectclass is printed after, sorted
             remaining attributes are printed after, sorted by key name.
             multiple values for an attribute are also sorted.
           Hence any valid unsorted ldif will comme out the same way from this 
           method'''

        #dn is always first
        #print 'dn:', ldapobject['dn']
        dn = ldapobject['dn'] 
        self.printAttributeAndValue(makePrintableAttributeAndValue('dn',dn))

        #Remove the attributes we already printed
        del ldapobject['dn']
        
        #This a changetype add, we add it
        self.printAttributeAndValue(makePrintableAttributeAndValue('changetype','add'))

        #Now with the object classes
        try:
            for objclass in sorted(ldapobject['objectclass']):
                self.printAttributeAndValue(makePrintableAttributeAndValue('objectclass',objclass))
            del ldapobject['objectclass']
        except KeyError:
            #object class is not mandatory
            pass

        large_attributes = []

        #This loops prints what is left
        for name in sorted(ldapobject.keys()):
            #Must check type instead of begging for forgiveness
            #because string is iterable but will not produce the
            #output we are looking for
            if isinstance(ldapobject[name], basestring):
                self.printAttributeAndValue(makePrintableAttributeAndValue(name,ldapobject[name]))
            else:
                #Print values prefixed with attribute name, sorted
                values = sorted(ldapobject[name])

                if len(values) > CHUNK_MAX_VALUES:
                    #TODO add another changetype: modify entry with the same dn
                    #(simply wrap the above into a question)
                    self.comment('Warning : there are {0} values for attribute name "{1}".'.format(len(values), name))
                    #Save the attribute for later (but we could just run the list again)
                    large_attributes.append(name)
                
                #Only so many attributes can fit in a LDIF record
                #TODO Put back the test of chunked values
                for value in values[:CHUNK_MAX_VALUES]:
                    self.printAttributeAndValue(makePrintableAttributeAndValue(name,value))
                
        #Ends with an empty line
        print >> self.ldiffile

        #For each attribute that had too many values
        for large_attribute in large_attributes:
            #Starting with the last entry we left out
            next_chunk = CHUNK_MAX_VALUES

            while ldapobject[large_attribute][next_chunk:next_chunk+CHUNK_MAX_VALUES]:
                #Output a changetype modify header
                self.printAttributeAndValue(makePrintableAttributeAndValue('dn',dn))
                self.printAttributeAndValue(makePrintableAttributeAndValue('changetype','modify'))
                self.printAttributeAndValue(makePrintableAttributeAndValue('add',large_attribute))

                #For each remaining value (which can also be chunked)
                for value in values[next_chunk:next_chunk+CHUNK_MAX_VALUES]:
                    self.printAttributeAndValue(makePrintableAttributeAndValue(large_attribute, value))

                #Ends with a separator
                print >> self.ldiffile, '-'
                #followed by an empty line
                print >> self.ldiffile
                
                next_chunk = next_chunk + CHUNK_MAX_VALUES
                
