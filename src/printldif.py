import argparse
import base64
import string
import textwrap


RFC2849_MAX_LINE = 76
CHUNK_MAX_VALUES = 1337

def RFC2849WrappedOuput(attribute, separator, value):
#def RFC2849WrappedOuput(attribute, separator, value):
    '''Wraps the value in a RFC2849 compliant manner.
    Returns a array of lines to print.'''
    wrapper = textwrap.TextWrapper()

    #Wrap length is the maximum line length, minus the leading space
    wrapper.width=RFC2849_MAX_LINE                        
    #We handle white space ourselves
    wrapper.drop_whitespace = False

    #The initial whitespace will be replaced by the attribute name
    #and ::, the encoded line separator, later on in this method
    wrapper.initial_indent=' '*(len(attribute)+len(separator)+1)

    #Other lines begin with a single space
    wrapper.subsequent_indent=' '

    #Wrap the whole thing
    lines = wrapper.wrap(value)
                                                
    #Remove the leading blank space with the attribute name
    lines[0] = attribute + separator + ' ' + lines[0].lstrip()
        
    #When we get here, we have it wrapped. But we might have been 
    #unlucky and end up with a line that ends (or begins with a 
    #space. Lets chechk for that.
    if any(l.startswith('  ') or l.endswith(' ') for l in lines):
        #We have a line that should be base64 encoded.
        #the separator is doubled (the attribute stays the same)
        #and the value is base64 encoded. This call is recursive
        #but a base64 coded value will never have a leading or
        #trailing space. It will always fail the test on the second
        #try
        lines = RFC2849WrappedOuput(attribute, separator*2, base64.b64encode(value))
        
    return lines


class LDIFPrinter(object):
    def __init__(self, ldiffile, overwrite, dontwrap, dontencode):
        self.ldiffile = ldiffile
        self.dontwrap = dontwrap
        self.dontencode = dontencode

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

        group.add_argument("-r",
                          "--dontwrap", dest="dontwrap",
                          action='store_true',
                          help="Will not wrap lines longer than 76 chars.")

        group.add_argument("-6",
                          "--dontencode", dest="dontencode",
                          action='store_true',
                          help="Do not base64 encode strings that a non-ascii caracters in them (will output utf-8 instead).")

        return parser

    @staticmethod
    def create(args):
        return LDIFPrinter(args.ldiffile, args.overwrite, args.dontwrap, args.dontencode)


    def comment(self, text):
        print >> self.ldiffile, '#', text


    def makePrintableAttributeAndValue(self, attribute, value):
        '''Makes a string with attribute and value.
        Makes shure that value contains only valid caracters. If not,
        the value is base64 encoded and the :: separator is used
        '''
        separator = ':'

        value = value.encode('utf-8')

        #Unless a flag was passed asking not to encode
        if not self.dontencode:
            #if it is has anything other than plain old ascii characters
            #(binary values like jpeg or certificates fall under this)
            if not all(ord(c) >= ord(' ') and ord(c) < 127 for c in value):
                separator = separator*2
                value = base64.b64encode(value)
            #And me make a special case with the password (obscurity)
            #FIXME Is this really worth it ? 
            elif attribute.lower() in ['userpassword', 'unicodePwd']:
                separator = separator*2
                value = base64.b64encode(value)
                
        return attribute, separator, value

        
    def printAttributeAndValue(self, attribute, separator, value):
        if self.dontwrap:
            print >> self.ldiffile, '\n'.join([attribute+separator+' '+value])
        else:
            print >> self.ldiffile, '\n'.join(RFC2849WrappedOuput(attribute, separator, value))


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
        attribute, separator, value = self.makePrintableAttributeAndValue('dn',dn)
        self.printAttributeAndValue(attribute, separator, value)

        #Remove the attributes we already printed
        del ldapobject['dn']
        
        #This a changetype add, we add it
        attribute, separator, value = self.makePrintableAttributeAndValue('changetype','add')
        self.printAttributeAndValue(attribute, separator, value)

        #Now with the object classes
        try:
            for objclass in sorted(ldapobject['objectclass']):
                attribute, separator, value = self.makePrintableAttributeAndValue('objectclass',objclass)
                self.printAttributeAndValue(attribute, separator, value)
            del ldapobject['objectclass']
        except KeyError:
            #object class is not mandatory
            pass

        large_attributes = {}

        #This loops prints what is left
        for name in sorted(ldapobject.keys()):
            #Must check type instead of begging for forgiveness
            #because string is iterable but will not produce the
            #output we are looking for
            if isinstance(ldapobject[name], basestring):
                attribute, separator, value = self.makePrintableAttributeAndValue(name,ldapobject[name])
                self.printAttributeAndValue(attribute, separator, value)
            else:
                #Print values prefixed with attribute name, sorted, unique
                values = sorted(set(ldapobject[name]))

                #Only so many attributes can fit in a LDIF record
                #TODO Put back the test of chunked values
                for value in values[:CHUNK_MAX_VALUES]:
                    attribute, separator, value = self.makePrintableAttributeAndValue(name,value)
                    self.printAttributeAndValue(attribute, separator, value)

                if len(values) > CHUNK_MAX_VALUES:
                    #TODO add another changetype: modify entry with the same dn
                    #(simply wrap the above into a question)
                    self.comment('Warning : there are {0} values for attribute name "{1}".'.format(len(values), name))
                    #Save the attribute for later (but we could just run the list again)
                    large_attributes[name] = values[CHUNK_MAX_VALUES:]

                
        #Ends with an empty line
        print >> self.ldiffile

        #For each attribute that had too many values
        for large_attribute, values in large_attributes.items():
            #Starting with the last entry we left out
            next_chunk = 0

            while values[next_chunk:next_chunk+CHUNK_MAX_VALUES]:
                #Output a changetype modify header
                attribute, separator, value = self.makePrintableAttributeAndValue('dn',dn)
                self.printAttributeAndValue(attribute, separator, value)
                attribute, separator, value = self.makePrintableAttributeAndValue('changetype','modify')
                self.printAttributeAndValue(attribute, separator, value)
                attribute, separator, value = self.makePrintableAttributeAndValue('add',large_attribute)
                self.printAttributeAndValue(attribute, separator, value)

                #For each remaining value (which can also be chunked)
                for value in values[next_chunk:next_chunk+CHUNK_MAX_VALUES]:
                    attribute, separator, value = self.makePrintableAttributeAndValue(large_attribute, value)
                    self.printAttributeAndValue(attribute, separator, value)

                #Ends with a separator
                print >> self.ldiffile, '-'
                #followed by an empty line
                print >> self.ldiffile
                
                next_chunk += CHUNK_MAX_VALUES
                
