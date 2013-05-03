import unittest
import sys

import utils

class ModuleTest(unittest.TestCase):

    def testPasswordGenerator(self):
        history = []
        length = 40

        generator = utils.PasswordGenerator(length)

        str(generator)
        
        #Make 100 random passwords, all different
        for n in xrange(0,100):
            password = str(generator)
            self.assertNotIn(password, history)
            history.append(password)

        #All password must be complex (50 chars)
        self.assertFalse(filter(lambda p: len(p) != length, history))

        #Such a short password will require many iterations to find
        #It will have one special, lower, upper and digit
        length = 4

        generator = utils.PasswordGenerator(length)
        
        #If we ever come back, we have our password
        self.assertTrue(len(str(generator)) == 4)
        
    def testComputePath(self):
        self.assertEqual('dc=example,dc=com', utils.compute_path('OU=somewhere,DC=example,DC=com'))
        self.assertEqual('', utils.compute_path('DC=com'))

    def testComputeParent(self):
        self.assertEqual('dc=com,dc=example', utils.compute_parent('CN=someone,DC=example,DC=com'))
        self.assertEqual('', utils.compute_parent('DC=com'))


if __name__ == "__main__":
    unittest.main()
