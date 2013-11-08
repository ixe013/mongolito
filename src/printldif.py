import base64
import os
import string
import textwrap
import sys

import basedestination
import factory

RFC2849_MAX_LINE = 76
CHUNK_MAX_VALUES = 1337

def RFC2849WrappedOutput(attribute, separator, value):
#def RFC2849WrappedOutput(attribute, separator, value):
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
    #(startswith 2 spaces because the 1st one is legit)
    if any(l.startswith('  ') or l.endswith(' ') for l in lines):
        #We have a line that should be base64 encoded.
        #the separator is doubled (the attribute stays the same)
        #and the value is base64 encoded. This call is recursive
        #but a base64 coded value will never have a leading or
        #trailing space. It will always fail the test on the second
        #try
        lines = RFC2849WrappedOutput(attribute, separator*2, base64.b64encode(value))
        
    return lines


class LDIFPrinter(basedestination.BaseDestination):
    def __init__(self, ldiffile=None, overwrite=True, dontwrap=True, dontencode=False, chunksize=CHUNK_MAX_VALUES):
        self.ldiffilename = ldiffile
        self.dontwrap = dontwrap
        self.dontencode = dontencode
        self.overwrite = overwrite
        self.chunksize = chunksize


    def connect(self):
        if self.ldiffilename is None:
            self.ldiffile = sys.stdout
        else:
            self.ldiffile = open(self.ldiffilename, 'a')
            if self.overwrite:
                self.ldiffile.truncate(0)

        return self

    def disconnect(self):
        if not self.ldiffilename is None:
            self.ldiffile.close()
        return self

    def comment(self, text):
        print >> self.ldiffile, '#', text


    def makePrintableAttributeAndValue(self, attribute, value):
        '''Makes a string with attribute and value.
        Makes shure that value contains only valid caracters. If not,
        the value is base64 encoded and the :: separator is used
        '''
        separator = ':'

        #FIXME : too much copy paste of code, refactor
        try:
            value = value.encode('utf-8')

            #Unless a flag was passed asking not to encode
            if not self.dontencode:
                #if it is has anything other than plain old ascii characters
                #(binary values like jpeg or certificates fall under this)
                if not all(ord(c) >= ord(' ') and ord(c) < 127 for c in value):
                    separator *= 2
                    value = base64.b64encode(value)
                #And me make a special case with the password (obscurity)
                #FIXME Is this really worth it ? 
                elif attribute.lower() in ['userpassword', 'unicodePwd']:
                    separator *= 2
                    value = base64.b64encode(value)
        except UnicodeError:
            separator *= 2
            value = base64.b64encode(value)
        except AttributeError as ae:
            raise ae
                
        return attribute, separator, value

        
    def printAttributeAndValue(self, attribute, separator, value):
        if self.dontwrap:
            print >> self.ldiffile, '\n'.join([attribute+separator+' '+value])
        else:
            print >> self.ldiffile, '\n'.join(RFC2849WrappedOutput(attribute, separator, value))


    def write(self, original, ldapobject):
        '''Prints a Python dict that represents a ldap object in a sorted matter
             dn is printed first
             objectclass is printed after, sorted
             remaining attributes are printed after, sorted by key name.
             multiple values for an attribute are also sorted.
           Hence any valid unsorted ldif will comme out the same way from this 
           method'''

        #FIXME : read only operations on ldapobject would save a lot of memory
        #        when working with large groups
        #working_copy = ldapobject.copy()
        working_copy = ldapobject

        #dn is always first
        #print 'dn:', working_copy['dn']
        dn = working_copy['dn'] 
        attribute, separator, value = self.makePrintableAttributeAndValue('dn',dn)
        self.printAttributeAndValue(attribute, separator, value)

        #Remove the attributes we already printed
        #del working_copy['dn']
        
        #Change type handling
        try:
            change = working_copy['changetype']
            attribute, separator, value = self.makePrintableAttributeAndValue('changetype',change)
            self.printAttributeAndValue(attribute, separator, value)

            #del working_copy['changetype']

            if change == 'modify':
                #If changetype is modify, then we have an attribute 
                #that is either replace, modify or delete
                if 'replace' in working_copy:
                    attribute, separator, value = self.makePrintableAttributeAndValue('replace',working_copy['replace'])
                    self.printAttributeAndValue(attribute, separator, value)
                    #del working_copy['replace']
                elif 'modify' in working_copy:
                    attribute, separator, value = self.makePrintableAttributeAndValue('modify',working_copy['modify'])
                    self.printAttributeAndValue(attribute, separator, value)
                    #del working_copy['modify']
            elif change == 'delete':
                #For a changetype delete, no other attributes are needed. The delete statement is
                #already printed, so the only thing left to do is to remove all other attributes
                #and let an empty dict fall through the code (for printing)
                working_copy = {}
                    
        except KeyError:
            #This a changetype add, we add it
            #Defaults to change type add
            attribute, separator, value = self.makePrintableAttributeAndValue('changetype','add')
            self.printAttributeAndValue(attribute, separator, value)

        #Now with the object classes
        try:
            objectclasses = working_copy['objectclass']

            if isinstance(objectclasses, basestring):
                objectclasses = [objectclasses]

            for objclass in sorted(objectclasses):
                attribute, separator, value = self.makePrintableAttributeAndValue('objectclass',objclass)
                self.printAttributeAndValue(attribute, separator, value)
            #del working_copy['objectclass']
        except KeyError:
            #object class is not mandatory
            pass

        large_attributes = {}

        #This loops prints what is left
        for name in sorted(working_copy.keys()):
            if name.lower() in ['dn', 'objectclass', 'changetype','replace', 'modify']:
                continue

            #Must check type instead of begging for forgiveness
            #because string is iterable but will not produce the
            #output we are looking for
            if isinstance(working_copy[name], basestring):
                attribute, separator, value = self.makePrintableAttributeAndValue(name,working_copy[name])
                self.printAttributeAndValue(attribute, separator, value)
            else:
                #Print values prefixed with attribute name, sorted, unique
                values = sorted(set(working_copy[name]))

                #Only so many attributes can fit in a LDIF record
                #TODO Put back the test of chunked values
                for value in values[:self.chunksize]:
                    attribute, separator, value = self.makePrintableAttributeAndValue(name,value)
                    self.printAttributeAndValue(attribute, separator, value)

                if len(values) > self.chunksize:
                    #TODO add another changetype: modify entry with the same dn
                    #(simply wrap the above into a question)
                    self.comment('Warning : there are {0} values for attribute name "{1}".'.format(len(values), name))
                    #Save the attribute for later (but we could just run the list again)
                    large_attributes[name] = values[self.chunksize:]

                
        #Ends with an empty line
        print >> self.ldiffile

        #For each attribute that had too many values
        for large_attribute, values in large_attributes.items():
            self.add_values_to_attribute(dn, large_attribute, values)
                
    def output(self, name, val):
        attribute, separator, value = self.makePrintableAttributeAndValue(name, val)
        self.printAttributeAndValue(attribute, separator, value)

    def add_values_to_attribute(self, dn, attribute, values):
        next_chunk = 0
        if isinstance(values, basestring):
            array_of_values = [values]
        else:
            array_of_values = values

        while array_of_values[next_chunk:next_chunk+self.chunksize]:
            #Output a changetype modify header
            self.output('dn', dn)
            self.output('changetype','modify')
            self.output('add', attribute)

            #For each remaining value (which can also be chunked)
            for value in array_of_values[next_chunk:next_chunk+self.chunksize]:
                self.output(attribute, value)

            #Ends with a separator
            print >> self.ldiffile, '-'
            #followed by an empty line
            print >> self.ldiffile
            
            next_chunk += self.chunksize


    def add(self, original, ldapobject):
        attributes_to_add = ldapobject['add']
        for attribute in attributes_to_add:
            ###### ICI LA VALEUR EST DECOUPEE EN CARACTERES ######
            self.add_values_to_attribute(ldapobject['dn'], attribute, ldapobject[attribute])


def create_from_uri(uri):
    '''
    Factory for LDIFPrinter
    '''    
    result = None
    
    root, ext = os.path.splitext(uri)

    if ext.lower() in ['.ldif', '.ldf']:
        result = LDIFPrinter(uri)

    return result

def create_undo_from_uri(uri):
    '''
    Factory for LDIFPrinter that writes to an undo file. Undo files
    can have any extension
    '''    
    return LDIFPrinter(uri)

#Boilerplate code to register this in the factory
factory.Factory().register(type(LDIFPrinter), create_from_uri)

