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
           'changeType: 0\n',
           '#Comment\n',
           'objectClass: top\n',
           'cn: Hello,\n',
           ' World\n',
           ' !\n',
           'version: 1,\n',
           'description:: R2Vzd\r',
           ' GlvbiBkZXMgZG9tYWluZXMgZGUgZMOpbMOpZ2F0aW9uLiBOZSBjb250aWVu\n',
           ' cyBwYXMgZGUgYmFzZXMgZGUgZG9ubsOpZXMu\n',
           'result: 0\n',
           'continue:\n',
           ' OnNextLine:\n',
           '#Trailing comments are ignored, not forwarded\n',
           '\n',
           'Remaining lines are left untouched\n',
           '\n',
        ]

        expectedLines = [
           'First line: asdf',
           'objectClass: top',
           'cn: Hello,World!',
           'version: 1',
           'description:: R2VzdGlvbiBkZXMgZG9tYWluZXMgZGUgZMOpbMOpZ2F0aW9uLiBOZSBjb250aWVucyBwYXMgZGUgYmFzZXMgZGUgZG9ubsOpZXMu',
           'result: 0',
           'continue: OnNextLine',
        ]
        
        linecount, readLines = readLDIF.extractLDIFFragment(rawLines)

        self.assertEqual(len(rawLines)-2, linecount, 'Line count does not match.')
        self.assertEqual(len(expectedLines), len(readLines), 'Missing or extra lines.')


    def testErrorReportingForFragments(self):
        '''Tests that exceptions are reported'''
        rawLines = [
            ' Starts with a space throws exception',
            #Processing stops, no need for a trailing \n
        ]
        
        self.assertRaises(importExceptions.LDIFParsingException, readLDIF.extractLDIFFragment, rawLines)


    def testConvertFragmentFeatures(self):
        parsedFragment = [
           'First;line: 8',
           'objectClass: top',
           'objectClass: user',
           'objectClass: person',
           'version: 1',
           'cn: Hello:World!',
           'description:: SidhaSBkw6lqw6AgdGVzdMOpIMOnYSBldCBqJ2FpIGTDqXRlc3TDqSDDp2E=',
           'category:: RU5SRUdJU1RSw4lF',
           'enable: TRUE',
        ]
        
        expectedDict = {
           'first;line':u'8',    #Converts to lowercase
           'objectclass':[u'top', u'user', u'person'],  #Makes an array
           'version':u'1',
           'cn':u'Hello:World!',
           'description':u"J'ai d\xe9j\xe0 test\xe9 \xe7a et j'ai d\xe9test\xe9 \xe7a",
           'category':u'ENREGISTR\xc9E',
           'enable':u'TRUE',
        }

        entry = readLDIF.convertLDIFFragment(parsedFragment)
 
        self.assertEqual(expectedDict, entry, 'Dictionary do not match')


if __name__ == "__main__":
    unittest.main()
