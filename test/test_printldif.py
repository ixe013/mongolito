import unittest

import printldif

class ModuleTest(unittest.TestCase):

    def testRFC2849WrappedOuput(self):
        attribute, separator, value = 'Hello', ':', 'World!'
                        
        #Basic line that doesn't need wrapping
        self.assertEquals([attribute+separator+' '+value], printldif.RFC2849WrappedOuput(attribute, separator, value))

        #Line that wraps 
        attribute, separator, value = 'test', ':', '1234567890'*8
        expected = ['test: 1234567890123456789012345678901234567890123456789012345678901234567890',
                    ' 1234567890']

        self.assertEquals(expected, printldif.RFC2849WrappedOuput(attribute, separator, value))

        #Line that wraps and is base64 encoded because of a space at the end
        attribute, separator, value = 'test', ':', '123456789 '*8
        expected = ['test:: MTIzNDU2Nzg5IDEyMzQ1Njc4OSAxMjM0NTY3ODkgMTIzNDU2Nzg5IDEyMzQ1Njc4OSAxM',
                     ' jM0NTY3ODkgMTIzNDU2Nzg5IDEyMzQ1Njc4OSA=']

        self.assertEquals(expected, printldif.RFC2849WrappedOuput(attribute, separator, value))


if __name__ == "__main__":
    unittest.main()
