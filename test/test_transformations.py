import copy
import unittest

import transformations
from transformations.addattribute import AddAttribute
from transformations.copyattribute import CopyAttribute
from transformations.copyfirstvalue import CopyFirstValueOfAttribute
from transformations.join import JoinMultiValueAttribute
from transformations.renameattribute import RenameAttribute
from transformations.renamevalue import RenameValue
from transformations.removeattribute import RemoveAttribute
from transformations.makevaluesunique import MakeValuesUnique
from transformations.mergeattributes import MergeAttributes
from transformations.removevalue import RemoveValue

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

    def testRemoveValue(self):
        ldapobject = {
            'single':'Hello',
            'cute':'Cat',
            'scary':['croCodile','Cobra'],
            'multi':['aaa','CCC','abracadabra'],
        }

        current = copy.deepcopy(ldapobject)

        #No match
        remover = RemoveValue('single', '/c/')
        remover.transform(ldapobject, current)

        #Match, remove attribute
        remover = RemoveValue('cute', '/c/')
        remover.transform(ldapobject, current)

        #Match on multiple, ends up removing the attribute
        remover = RemoveValue('scary', '/c/')
        remover.transform(ldapobject, current)

        #Match on some attribute, leaves a single valued attribute
        remover = RemoveValue('multi', '/c/')
        remover.transform(ldapobject, current)

        expected = {
            'single':'Hello',
            'multi':'aaa',
        }

        self.assertEquals(current, expected)


    def testAddAttribute(self):
        adder = AddAttribute('userPassword', 'coucou')
    
        original = {}
        ldapobject = {}

        #Add the first attribute
        adder.transform(original, ldapobject)
        self.assertIn('userPassword', ldapobject.keys(), 'Attribute not found in dict')
        self.assertIsInstance(ldapobject['userPassword'], str, 'Attribute should be a string')
        self.assertEquals(ldapobject['userPassword'], 'coucou', 'Attribute value was not set properly.')
        
        #Make the attribute multi valued
        adder.transform(original, ldapobject)
        self.assertIsInstance(ldapobject['userPassword'], list, 'Attribute should be multi-valued')

        #Add to a multi-value
        adder.transform(original, ldapobject)
        self.assertIsInstance(ldapobject['userPassword'], list, 'Attribute should be multi-valued')
        self.assertTrue(len(ldapobject['userPassword']) == 3)


    def testMakeAttributesUnique(self):
        ldapobject = {
            'dn':'cn=coucou',
            'objectClass': [ 'top', 'person', 'top', 'top', 'person', 'top' ]
        }

        original = copy.deepcopy(ldapobject)

        merger = MakeValuesUnique('objectClass')

        ldapobject = merger.transform(original, ldapobject)

        self.assertIsInstance(ldapobject['objectClass'], list, 'objectClass should still be multi valued')
        self.assertIn('top', ldapobject['objectClass'], 'objectClass top is gone')
        self.assertIn('person', ldapobject['objectClass'], 'objectClass person is gone')
        self.assertTrue(len(ldapobject['objectClass']) == 2)


        backup = ldapobject

        merger.transform(original, ldapobject)
        self.assertEquals(backup, ldapobject, 'merged object should not have changed')
        

        ldapobject['objectClass'] = [ 'top', 'top', 'top' ]

        merger.transform(original, ldapobject)
        self.assertIsInstance(ldapobject['objectClass'], str)


    def testCopyFirstValueOfAttribute(self):
        ldapobject = {
            'dn':'cn=coucou',
            'single': 'aaa',
            'multi': ['1', '2']
        }

        current = copy.deepcopy(ldapobject)

        copyer = CopyFirstValueOfAttribute('single', 'copied-from-single')

        #Copy single to none
        copyer.transform(ldapobject, current)
        #Copy single to single
        copyer.transform(ldapobject, current)
        #Copy single to multi
        copyer.transform(ldapobject, current)

        copyer = CopyFirstValueOfAttribute('multi', 'copied-from-multi')

        #Copy first value of multi to none
        copyer.transform(ldapobject, current)
        #Copy first value of multi to single
        copyer.transform(ldapobject, current)
        #Copy first value of multi to multi
        copyer.transform(ldapobject, current)

        expected = {
            'dn':'cn=coucou',
            'single': 'aaa',
            'copied-from-single': ['aaa', 'aaa', 'aaa'],
            'multi': ['1', '2'],
            'copied-from-multi': ['1', '1', '1' ]
        }

        self.assertEqual(current, expected)

    def testCopyAttribute(self):
        ldapobject = {
            'dn':'cn=coucou',
            'single': 'aaa',
            'multi': ['111','222','333'],
        }

        current = copy.deepcopy(ldapobject)

        copier = CopyAttribute('single','single-copy')
        copier.transform(ldapobject, current)

        copier = CopyAttribute('multi','multi-copy')
        copier.transform(ldapobject, current)

        expected = {
            'dn':'cn=coucou',
            'single': 'aaa',
            'multi': ['111','222','333'],
            'single-copy':'aaa',
            'multi-copy': ['111','222','333'],
        }

        self.assertEqual(current,expected)

    def testRenameValue(self):
        ldapobject = {
            'dn':'ou=people,ou=example,ou=com',
            'ou':'people',
            'single':'abracadabra',
            'multi':['abracadabra', 'apple', 'cat', 'sky'],
            'untouched':'blah'
        }
        
        current = copy.deepcopy(ldapobject)

        #Changing the DN propagates to the attribute that design the
        #first component
        renamer = RenameValue('dn', 'ou=people,ou=example,ou=com', r'ou=aliens,ou=example,ou=com')
        renamer.transform(ldapobject, current)

        #Regular expression on a single value  a --> 4
        renamer = RenameValue('single', '/[a]/', '4')
        renamer.transform(ldapobject, current)

        #Regular expression on a multi value  a --> 4
        renamer = RenameValue('multi', '/[a]/', '4')
        renamer.transform(ldapobject, current)

        renamer = RenameValue('multi', '/[k]/', '|<')
        renamer.transform(ldapobject, current)

        expected = {
            'dn':'ou=aliens,ou=example,ou=com',
            'ou':'aliens',
            'single':'4br4c4d4br4',
            'multi':['4br4c4d4br4', '4pple', 'c4t', 's|<y'],
            'untouched':'blah'
        }

        self.assertEqual(expected, current)

    def testRenameAttribute(self):
        #TODO
        pass

    def testRemoveAttribute(self):
        ldapobject = {
            'dn':'cn=coucou',
            'single': 'aaa',
            'multi': ['1', '2']
        }

        current = copy.deepcopy(ldapobject)

        remover = RemoveAttribute('single')
        remover.transform(ldapobject, current)

        remover = RemoveAttribute('multi')
        remover.transform(ldapobject, current)
 
        expected = {
            'dn':'cn=coucou',
        }

        self.assertEqual(current, expected)

    def testJoinMultiValueAttribute(self):
        ldapobject = {
            'multi': ['1', '2', '3']
        }

        current = copy.deepcopy(ldapobject)

        joiner = JoinMultiValueAttribute('multi',' - ', 'flat')
        joiner.transform(ldapobject, current)

        expected = {
            'multi': ['1', '2', '3'],
            'flat': '1 - 2 - 3'
        }

        self.assertEquals(current, expected)

    def testMergeAttributes(self):
        ldapobject = {
            'cn':'blah',
            'uniqueMember':'dude',
            'equivalentToMe':['john','doe'],
        }

        original = copy.deepcopy(ldapobject)

        #Merge uniqueMember and equivalentToMe in member
        merger = MergeAttributes('member', 'uniqueMember', 'equivalentToMe')
        merger.transform(original, ldapobject)

        ldapobject['member'].sort()

        expected = {
            'cn':'blah',
            'member':['doe','dude','john']
        }

        self.assertEquals(expected, ldapobject)

        ldapobject = {
            'cn':'blah',
            'member':'ada',
            'uniqueMember':'dude',
            'equivalentToMe':['john','doe', 'ada'],
        }

        #Merge uniqueMember and equivalentToMe with existing member
        merger = MergeAttributes('member', 'uniqueMember', 'equivalentToMe', 'member')
        merger.transform(original, ldapobject)

        #In this trivial, merging attributes is like a rename
        merger = MergeAttributes('zzz', 'cn', 'does-not-exists')
        merger.transform(original, ldapobject)

        ldapobject['member'].sort()

        expected = {
            'zzz':'blah',
            'member':['ada','doe','dude','john']
        }

        self.assertEquals(expected, ldapobject)


if __name__ == "__main__":
    unittest.main()
