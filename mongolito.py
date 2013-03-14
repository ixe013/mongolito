import sys
from optparse import OptionParser

import ldif2dict
import printldif
import importExceptions


usage = "usage: %prog [options] arg1 arg2"
parser = OptionParser(usage=usage)

parser.add_option("-f", 
                  "--file", dest="filename",
                  help="The LDIF file to import", 
                  metavar="FILENAME")


#Parse the command line
(options, args) = parser.parse_args()

def main():
    input_stream = sys.stdin

    if not options.filename == None:
        input_stream = open(options.filename, "r")

    #Prime the pump by reading a first entry
    lineCount, lines = ldif2dict.extractLDIFFragment(input_stream, 0)

    try:
        #As long as we are not done with the file
        while(len(lines) > 0):
            try:
                #convert the raw lines to a Python dict (easier to parse)
                ldapObject = ldif2dict.convertLDIFFragment(lines)
                #Print, sorted. 
                printldif.printDictAsLDIF(ldapObject)

                #Read the next object
                c, lines = ldif2dict.extractLDIFFragment(input_stream, lineCount)

                lineCount += c

            except importExceptions.LDIFParsingException as lpe:
                print >> sys.stderr, lpe
                break

    except:
        print 'Stopped at line %d', lineCount
            

        
    if options.filename != None:
        input_stream.close()


if __name__ == "__main__":
    main()

