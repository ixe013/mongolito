import unittest

import insensitivedict

class ModuleTest(unittest.TestCase):

    def testCaseInsensitiveKey(self):
        somedict = insensitivedict.InsensitiveDict({'xyz': 2, 'wMa': 8, 'Pma': 9})
        somedict['AAA'] = 1

        #Get None when looking for an inexisting key
        self.assertEqual(None, somedict.get('asdf'))
    
        #Get the right value looking for an wrong cased key
        self.assertEqual(2, somedict['XYZ'])

        #Raise on missing key
        with self.assertRaises(KeyError):
            somedict['asdf']

