'''
Reads in a bunch of LDIF lines, making a dict out of it. Base64 encoded values are
removed, and duplicate attributes are turned into an array. After a whole object has
been read, this function returns. 

Example : The following ldif fragment
   dn: cn=hello
   objectClass: top
   objectClass: user
   cn: hello
   description: SnVzdGF0ZXN0Lg==

Will produce the following Python dict :
{ 'dn':'cn=hello',
 'objectClass':['top','user'],
 'cn':'hello',
 'description':'Just a test.' }
'''
import base64
import importExceptions
import argparse


def addArguments(parser):
    group = parser.add_argument_group('Import LDIF file')
    group.add_argument("-l",
                      "--ldif", dest="ldiffile",
                      type=argparse.FileType('r'),
                      help="The LDIF file to import. Use - for stdin")

    return parser

 
def extractLDIFFragment(inputStream, lineNumber=0):
    '''Reads a LDIF file, stopping at the first blank line.
       This function :
         - ignores comments.
         - merges lines that were split into a single line
         - does not decode base64 encoded values
       '''
    lines = []
    lastLineWasIgnored = False
    leadingAttributesToIgnore = [
      'result:', 
      'search: ', 
      'version: ', 
    ]

    for line in inputStream:
        #Simple line counter
        lineNumber += 1

        #Did we just hit a blank line ?
        if line.isspace():
            if len(lines) == 0:
                #Leading blank lines are ignored
                continue
            else:
                #Found the end of the fragment
                break
            
        #If this is a comment
        elif line[0] == '#':
            #It might be multi-line
            lastLineWasIgnored = True
            #Leave it alone (ignore it)
            continue

        #Is this line the continuation of the previous line ?
        elif not line.startswith(' '):
            #Ignore leading version, but only if it is
            #the first item in the fragment
            if filter(line.lower().startswith, leadingAttributesToIgnore) and len(lines) == 0:
                lastLineWasIgnored = True
                continue
            #or if it is a changetype directive
            if line.lower().startswith('changetype:'):
                lastLineWasIgnored = True
                continue
                
            #(bring 8 bit ascii values in the utf8 world)
            line = line.decode('latin_1').encode('utf-8')
            #It is a new attribute:value pair, save it
            lines.append( line.strip() )
            

        #If the last line was a comment...
        elif lastLineWasIgnored:
            #Then we just hit a multi line comment
            #We don't reset lastLineWasIgnored, we are still ignoring!
            continue
        

        elif len(lines) > 0:
            #(bring 8 bit ascii values in the utf8 world first)
            line = line.decode('latin_1').encode('utf-8')
            #Append this to the last line
            lines[len(lines)-1] += line.strip()

        else:
            raise importExceptions.LDIFParsingException(lineNumber, line.rstrip(), 'LDIF fragment starts with space')

        lastLineWasIgnored = False

    
    return (lineNumber, lines)


def convertLDIFFragment(fragment):
    '''Converts a fragment to a dictionary. It will :
          - convert attribute names to lowercase
          - create a list of values if an attribute has multiple values '''
    ldapObject = {}

    for line in fragment:
        #Split the attribute name from the value
        attribute, value = line.split(':',1)
        
        #Attributes are converted to lowercase
        attribute = attribute.lower()

        #Is this value base64 encoded ?
        if value[:1] == ':':
            #Decode to a UTF-8 encoded Unicode String
            value = base64.b64decode(value[1:].strip())
        else:
            #String leading white space
            value = value.strip()

        #Multiple attributes are turned into an array
        if attribute in ldapObject.keys(): 
            #If we already have an array
            if type(ldapObject[attribute]) == type([]):
                #Simply append
                ldapObject[attribute].append(value)
            else:
                #This is the second attribute, make it an array
                ldapObject[attribute] = [ldapObject[attribute], value]
        else:
            #First occurence of this attribute for this object
            ldapObject[attribute] = value

    return ldapObject
        
