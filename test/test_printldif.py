import unittest

import printldif

class ModuleTest(unittest.TestCase):

    def testRFC2849WrappedOuput(self):
        rawline = 'Hello: World!'

        for line in printldif.RFC2849WrappedOuput(rawline):
            self.assertTrue(len(line)<=76, 'Line not wrapped (%d chars, %s)' % (len(line), line))

        rawline = rawline * 15


if __name__ == "__main__":
    unittest.main()
