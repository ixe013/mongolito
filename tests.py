import unittest

import ldif2dict
import importExceptions
import printldif

class MyTest(unittest.TestCase):
    def testReadFragmentFeatures(self):
        '''Tests all the parsing features'''
        rawLines = [
           '\n',
           '\n',
           'version: version attribute is ignored if first in fragment\n',
           '\n',
           'SEARCH: ignored, case insensitive\n',
           'result: \n'
           '\n',
           '#This is a special\n',
           ' multi-line comment\n',
           ' with a lot of lines\n',
           'First line\n',
           '#Comment\n',
           'objectClass: top\n',
           'cn: Hello,\n',
           ' World\n',
           ' !\n',
           'version: 1,\n',
           'description: SnVzdGF0ZXN0Lg==\n',
           'result: 0\n',
           'continue:\n',
           ' OnNextLine:\n',
           '#Trailing comments are ignored, not forwarded\n',
           '\n',
           'Remaining lines are left untouched\n',
           '\n',
        ]
        
        expectedLines = [
           'First line',
           'objectClass: top',
           'cn: Hello,World!',
           'version: 1',
           'description: SnVzdGF0ZXN0Lg==',
           'result: 0',
           'continue: OnNextLine',
        ]
        
        linecount, readLines = ldif2dict.extractLDIFFragment(rawLines)

        self.assertEqual(len(rawLines)-2, linecount, 'Line count does not match.')
        self.assertEqual(len(expectedLines), len(readLines), 'Missing or extra lines.')


    def testErrorReportingForFragments(self):
        '''Tests that exceptions are reported'''
        rawLines = [
            ' Starts with a space throws exception',
            #Processing stops, no need for a trailing \n
        ]
        
        self.assertRaises(importExceptions.LDIFParsingException, ldif2dict.extractLDIFFragment, rawLines)


    def testConvertFragmentFeatures(self):
        parsedFragment = [
           'First;line: 8',
           'objectClass: top',
           'objectClass: user',
           'objectClass: person',
           'version: 1',
           'cn: Hello:World!',
           'description: SnVzdGF0ZXN0Lg==',
           'enable: TRUE',
        ]
        
        expectedDict = {
           'first;line':'8',    #Converts to lowercase
           'objectclass':['top', 'user', 'person'],  #Makes an array
           'version':'1',
           'cn':'Hello:World!',
           'description':'SnVzdGF0ZXN0Lg==',
           'enable':'TRUE',
        }

        entry = ldif2dict.convertLDIFFragment(parsedFragment)

        #self.assertEqual(expectedDict, entry, 'Dictionary do not match')
        self.assertEqual(expectedDict, entry, 'Dictionary do not match')

    def testPrint(self):
        expectedDict = {
           'dn':'test',
           'first;line':'8',    #Converts to lowercase
           'objectclass':['top', 'user', 'person'],  #Makes an array
           'version':'1',
           'cn':'Hello:World!',
           'description':'SnVzdGF0ZXN0Lg==',
           'uniquemember':['cn=orcladmin,cn=users,dc=delegation,dc=qc,dc=ca', 'cn=orcladmin,cn=users,dc=ireq,dc=qc,dc=ca', 'cn=reportsapp,cn=products,cn=oraclecontext,dc=ireq,dc=qc,dc=ca'],
           'enable':'TRUE',
        }

        #printldif.printDictAsLDIF(expectedDict)


if __name__ == "__main__":
    unittest.main()
