import unittest

import transformations

class ModuleTest(unittest.TestCase):

    def testAddValue(self):
        #Add a single value to None
        self.assertEquals('a', transformations.add_value(None, 'a'))

        #Add a single value to a single value
        newval = transformations.add_value('a', 'b')
        newval.sort()
        self.assertEquals(['a', 'b'], newval)

        #Add a single value to a multi value 
        newval = transformations.add_value(['a', 'c'], 'b')
        newval.sort()
        self.assertEquals(['a', 'b', 'c'], newval)

        #Add a multi value to a single value 
        newval = transformations.add_value('a', ['b', 'd'])
        newval.sort()
        self.assertEquals(['a', 'b', 'd'], newval)

        #Add a multi value to a multi value 
        newval = transformations.add_value(['a', 'c'], ['b', 'd'])
        newval.sort()
        self.assertEquals(['a', 'b', 'c', 'd'], newval)

    def testAddAttribute(self):
        adder = transformations.AddAttribute('userPassword', 'coucou')
    
        ldapobject = {}

        #Add the first attribute
        adder([ldapobject]).next()
        self.assertIn('userPassword', ldapobject.keys(), 'Attribute not found in dict')
        self.assertIsInstance(ldapobject['userPassword'], str, 'Attribute should be a string')
        self.assertEquals(ldapobject['userPassword'], 'coucou', 'Attribute value was not set properly.')
        
        #Make the attribute multi valued
        adder([ldapobject]).next()
        self.assertIsInstance(ldapobject['userPassword'], list, 'Attribute should be multi-valued')

        #Add to a multi-value
        adder([ldapobject]).next()
        self.assertIsInstance(ldapobject['userPassword'], list, 'Attribute should be multi-valued')
        self.assertTrue(len(ldapobject['userPassword']) == 3)

    def testMakeAttributesUnique(self):
        ldapobject = {
            'dn':'cn=coucou',
            'objectClass': [ 'top', 'person', 'top', 'top', 'person', 'top' ]
        }

        merger = transformations.MakeValuesUnique('objectClass')

        ldapobject = merger([ldapobject]).next()

        self.assertIsInstance(ldapobject['objectClass'], list, 'objectClass should still be multi valued')
        self.assertIn('top', ldapobject['objectClass'], 'objectClass top is gone')
        self.assertIn('person', ldapobject['objectClass'], 'objectClass person is gone')
        self.assertTrue(len(ldapobject['objectClass']) == 2)


        backup = ldapobject

        merger([ldapobject]).next()
        self.assertEquals(backup, ldapobject, 'merged object should not have changed')
        

        ldapobject['objectClass'] = [ 'top', 'top', 'top' ]

        merger([ldapobject]).next()
        self.assertIsInstance(ldapobject['objectClass'], str)

    def testCopyFirstValueOfAttribute(self):
        ldapobject = {
            'dn':'cn=coucou',
            'single': 'aaa',
            'multi': ['1', '2']
        }

        copyer = transformations.CopyFirstValueOfAttribute('single', 'copied-from-single')

        #Copy single to none
        copyer([ldapobject]).next()
        #Copy single to single
        copyer([ldapobject]).next()
        #Copy single to multi
        copyer([ldapobject]).next()

        copyer = transformations.CopyFirstValueOfAttribute('multi', 'copied-from-multi')

        #Copy first value of multi to none
        copyer([ldapobject]).next()
        #Copy first value of multi to single
        copyer([ldapobject]).next()
        #Copy first value of multi to multi
        copyer([ldapobject]).next()

        expected = {
            'dn':'cn=coucou',
            'single': 'aaa',
            'copied-from-single': ['aaa', 'aaa', 'aaa'],
            'multi': ['1', '2'],
            'copied-from-multi': ['1', '1', '1' ]
        }

        self.assertEqual(ldapobject, expected)

    def testRemoveAttribute(self):
        ldapobject = {
            'dn':'cn=coucou',
            'single': 'aaa',
            'multi': ['1', '2']
        }

        remover = transformations.RemoveAttribute('single')
        remover([ldapobject]).next()

        remover = transformations.RemoveAttribute('multi')
        remover([ldapobject]).next()
 
        expected = {
            'dn':'cn=coucou',
        }

        self.assertEqual(ldapobject, expected)


if __name__ == "__main__":
    unittest.main()
