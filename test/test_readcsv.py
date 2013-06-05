import unittest

import readCSV

class MyTest(unittest.TestCase):
    def testCSV(self):
        '''The CSV features'''
        rawcsv = ['dn:objectClass:cn',
                  'cn=aaa,dc=example,dc=com:inetOrgPerson|top:aaa', 
                  'cn=bbb,dc=example,dc=com:inetOrgPerson|top:bbb' ]

        expected = [
            { 'dn':'cn=aaa,dc=example,dc=com',
              'objectClass':['inetOrgPerson','top'],
              'cn':'aaa' },
            { 'dn':'cn=bbb,dc=example,dc=com',
              'objectClass':['inetOrgPerson','top'],
              'cn':'bbb' },
        ]
        
        reader = readCSV.CSVReader(rawcsv, ':', '|')

        found = reader.search()

        for i, ldapobject in enumerate(found):
            self.assertEqual(expected[i], ldapobject)


if __name__ == "__main__":
    unittest.main()
