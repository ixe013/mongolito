import sys
from optparse import OptionParser

import LDIF2Python


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

    if options.filename == None:
        print 'Reading from STDIN...'
    else:
        input_stream = open(options.filename, "r")

    lines = LDIF2Python.extractLDIFFragment(input_stream)

    while(len(lines) > 0):
        for s in lines:
            print s

        lines = LDIF2Python.extractLDIFFragment(input_stream)
        print '----8<--- END OF FRAGMENT -----8<------'
        
    if options.filename != None:
        input_stream.close()


if __name__ == "__main__":
    main()

