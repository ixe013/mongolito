import unittest
import sys

import utils

class ModuleTest(unittest.TestCase):

    def testPasswordGenerator(self):
        generator = utils.PasswordGenerator()

        history = []

        #Make 100 random passwords, all different
        for n in xrange(0,100):
            password = str(generator)
            self.assertNotIn(password, history)
            history.append(password)

        #All password must be complex (50 chars)
        self.assertFalse(filter(lambda p: len(p) != 50, history))


if __name__ == "__main__":
    unittest.main()
