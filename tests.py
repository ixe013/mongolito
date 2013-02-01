import unittest
import ldif2dict

class MyTest(unittest.TestCase):
    def testReadFragmentFeatures(self):
        rawLines = [
           'First line\n',
           '#Comment\n',
           'objectClass: top\n',
           'cn: Hello,\n',
           ' World!\n',
           'description: SnVzdGF0ZXN0Lg==\n',
           '\n'
        ]
        
        expectedLines = [
           'First line',
           'objectClass: top',
           'cn: Hello,World!',
           'description: SnVzdGF0ZXN0Lg==',
        ]
        
        readLines = ldif2dict.extractLDIFFragment(rawLines)

        self.assertEqual(len(expectedLines), len(readLines))
        

if __name__ == "__main__":
    unittest.main()
