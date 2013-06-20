import unittest
import collections

import readLDAP

class MyTest(unittest.TestCase):
    def testCreate(self):
        reader = readLDAP.LDAPReader.create_from_uri('', 'ldap://192.168.2.151/dc=directory,dc=example,dc=com')

    def testConvertQuery(self):
        reader = readLDAP.LDAPReader.create_from_uri('', 'ldap://192.168.2.151/dc=directory,dc=example,dc=com')

        query = collections.OrderedDict()

        query['objectClass'] = ['top','user']
        query['cn'] = 'dude'
        query['loginDisabled'] = 'TRUE'

        base, filt = reader.convert_query(query)

        self.assertEqual(base, 'dc=directory,dc=example,dc=com')
        self.assertEqual(filt, r'(&(objectClass=top)(objectClass=user)(cn=dude)(loginDisabled=TRUE))')

    def testConvertMetadataQuery(self):
        reader = readLDAP.LDAPReader.create_from_uri('', 'ldap://192.168.2.151/dc=directory,dc=example,dc=com')

        query = collections.OrderedDict()

        query['objectClass'] = ['top','user']
        query['mongolito.rdn'] = 'dude'
        query['mongolito.parent'] = 'ou=users'
        query['mongolito.path'] = 'dc=com,dc=example,dc=directory'

        base, filt = reader.convert_query(query)

        self.assertEqual(base, r'dc=directory,dc=example,dc=com')
        self.assertEqual(filt, r'(&(objectClass=top)(objectClass=user)(|(cn=Dude)(uid=Dude)))')

        query = collections.OrderedDict()

        query['objectClass'] = ['top','user']
        query['mongolito.rdn'] = 'dude'
        query['mongolito.parent'] = 'ou=users'
        query['mongolito.path'] = '/^dc=com,dc=example'

        base, filt = reader.convert_query(query)

        self.assertEqual(base, r'dc=example,dc=com')
        self.assertEqual(filt, r'(&(objectClass=top)(objectClass=user)(|(cn=Dude)(uid=Dude)))')

if __name__ == "__main__":
    unittest.main()
