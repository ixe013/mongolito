import base64
import unittest
import sys

import utils

class ModuleTest(unittest.TestCase):

    def testPasswordGenerator(self):
        history = []
        length = 40

        generator = utils.RandomPasswordGenerator(length)

        #Can be used like this
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

        generator = utils.RandomPasswordGenerator(length)
        
        #If we ever come back, we have our password
        self.assertTrue(len(str(generator)) == 4)
        

    def testUnicodePasswordGenerator(self):
        generator = utils.RandomUnicodePasswordGenerator(len('newPassword'))
        
        encodedPassword = base64.b64encode(str(generator))
        
        #I only check the length
        self.assertEqual(len(encodedPassword), len('IgBuAGUAdwBQAGEAcwBzAHcAbwByAGQAIgA='))
        

    def testComputePath(self):
        self.assertEqual('dc=example,dc=com', utils.compute_path('OU=somewhere,DC=example,DC=com'))
        self.assertEqual('', utils.compute_path('DC=com'))

    def testComputeParent(self):
        self.assertEqual('dc=com,dc=example', utils.compute_parent('CN=someone,DC=example,DC=com'))
        self.assertEqual('', utils.compute_parent('DC=com'))

    def testConvertRegex(self):
        pattern1 = '/hello$/'
        pattern2 = '/^world/i'
        pattern3 = 'meow'

        #Case insentive by default
        regex1 = { '$regex':'hello$', '$options':'i' }
        self.assertEquals(regex1, utils.regex_from_javascript(pattern1))

        #insensitive flag wins, trailing i is ignored
        regex2 = { '$regex':'^world' }
        self.assertEquals(regex2, utils.regex_from_javascript(pattern2, False))

        #a string defaults to a case insensitive pattern
        regex3 = { '$regex':'meow', '$options':'i' }
        self.assertEquals(regex3, utils.regex_from_javascript(pattern3))

    def testGetNestedAttribute(self):
        ldapobject = {
            'regular':1,
            'a':{'nested':{'key':3}},
        }

        #Defaults to regular dict 
        self.assertEquals(ldapobject['regular'], utils.get_nested_attribute(ldapobject, 'regular'))

        #Key error on missing regular key
        with self.assertRaises(KeyError):
            utils.get_nested_attribute(ldapobject, 'asdf')

        #Nested key
        self.assertEquals(ldapobject['a']['nested']['key'], utils.get_nested_attribute(ldapobject, 'a.nested.key'))

        #Key error on missing nested key
        with self.assertRaises(KeyError):
            utils.get_nested_attribute(ldapobject, 'a.s.d.f')


if __name__ == "__main__":
    unittest.main()
