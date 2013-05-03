import unittest

import readLDIF
import importExceptions

class MyTest(unittest.TestCase):
    def testReadFragmentFeatures(self):
        '''Tests all the parsing features'''
        rawLines = [
           '\n',
           '\n',
           'version: version attribute is ignored if first in fragment\n',
           ' it could as well be a multi-line version. The following \n',
           ' blank line is also ignored. \n',
           '\n',
           'SEARCH: ignored, case insensitive\n',
           'result: \n'
           '\n',
           '#This is a special\n',
           ' multi-line comment\n',
           ' with a lot of lines\n',
           'First line: asdf\n',
           'changetype: add\n',
           '#Comment\n',
           'objectClass: top\n',
           'cn: Hello,\n',
           ' World\n',
           ' !\n',
           'version: 1\n',
           'description:: R2VzdGlvbiBkZXMgZG9tYWluZXMgZ\n',
           ' GUgZMOpbMOpZ2F0aW9uLiBOZSBjb250aWVucyBwYXM\n',
           ' gZGUgYmFzZXMgZGUgZG9ubsOpZXMu\n',
           'result: 0\n',
           'continue:\n',
           ' OnNextLine\n',
           '#Trailing comments are ignored, not forwarded\n',
           '\n',
           'Remaining lines are left untouched\n',
           '\n',
        ]

        expected_lines = [
           'First line: asdf',
           'changetype: add',
           'objectClass: top',
           'cn: Hello,World!',
           'version: 1',
           'description:: R2VzdGlvbiBkZXMgZG9tYWluZXMgZGUgZMOpbMOpZ2F0aW9uLiBOZSBjb250aWVucyBwYXMgZGUgYmFzZXMgZGUgZG9ubsOpZXMu',
           'result: 0',
           'continue: OnNextLine',
        ]
        
        linecount, read_lines = readLDIF.extractLDIFFragment(rawLines)

        self.assertEqual(expected_lines, read_lines)


    def testErrorReportingForFragments(self):
        '''Tests that exceptions are reported'''
        rawLines = [
            ' Starts with a space throws exception',
            #Processing stops, no need for a trailing \n
        ]
        
        #self.assertRaises(importExceptions.LDIFParsingException, readLDIF.extractLDIFFragment, rawLines)


    def testConvertFragmentFeatures(self):
        """Verifies that a parsed fragment is properly turned into a Python dict"""
        parsedFragment = [
           'First;line: 8',
           'objectClass: top',
           'objectClass: user',
           'objectClass: person',
           'version: 1',
           'cn: Hello:World!',
           'description:: SidhaSBkw6lqw6AgdGVzdMOpIMOnYSBldCBqJ2FpIGTDqXRlc3TDqSDDp2E=',
           'category:: 5Za25qWt6YOo',
           'enable: TRUE',
        ]
        
        expectedDict = {
           'first;line':'8',    #Converts to lowercase
           'objectclass':['top', 'user', 'person'],  #Makes an array
           'version':'1',
           'cn':'Hello:World!',
           'description':"J'ai d\xc3\xa9j\xc3\xa0 test\xc3\xa9 \xc3\xa7a et j'ai d\xc3\xa9test\xc3\xa9 \xc3\xa7a",
           'category':'\xe5\x96\xb6\xe6\xa5\xad\xe9\x83\xa8',
           'enable':'TRUE',
        }

        #entry = readLDIF.convertLDIFFragment(parsedFragment)
 
        #self.assertEqual(expectedDict, entry, 'Dictionary do not match')


if __name__ == "__main__":
    unittest.main()
