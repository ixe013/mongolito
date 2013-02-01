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

def extractLDIFFragment(input):
    '''Reads a LDIF file, stopping at the first blank line.
       This function :
         - ignores comments.
         - merges lines that were split into a single line
         - does not decode base64 encoded values
       '''
    lines = []

    for line in input:
        #Did we just hit a blank line ?
        if line.isspace():
            #Found the end of the fragment
            break
        #If this is a comment
        elif line[0] == '#':
            #Leave it alone
            continue

        #Is this line the continuation of the previous line ?
        elif not line.find(' ') == 0:
            #It is a new attribute:value pair, save it
            lines.append( line.strip() )
            continue

        elif len(lines) > 0:
            #Append this to the last line
            lines[len(lines)-1] += line.strip()

        else:
            #raise 'LDIF fragment starts with continuation line'
            print 'LDIF fragment starts with continuation line'
            break
    
    return lines


