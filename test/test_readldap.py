import unittest
import collections

import readLDAP

class MyTest(unittest.TestCase):
    def testCreate(self):
        reader = readLDAP.LDAPReader.create_from_uri('', 'ldap://192.168.2.151/dc=directory,dc=example,dc=com')

    def testConvertQuery(self):
        reader = readLDAP.LDAPReader.create_from_uri('', 'ldap://192.168.2.151/dc=directory,dc=example,dc=com')

        query = collections.OrderedDict()

        query['objectClass'] = ['user','userProxyFull']
        query['cn'] = 'dude'
        query['loginDisabled'] = 'TRUE'

        base, filt = reader.convert_query(query)

        self.assertEqual(base, 'dc=directory,dc=example,dc=com')
        self.assertEqual(filt, '(&(|(objectClass=user)(objectClass=userProxyFull))(cn=dude)(loginDisabled=TRUE))')

    def testConvertMetadataQuery(self):
        reader = readLDAP.LDAPReader.create_from_uri('', 'ldap://192.168.2.151/dc=directory,dc=example,dc=com')

        query = collections.OrderedDict()

        query['objectClass'] = ['userProxyFull','user']
        query['description'] = 'Hello*'
        query['mongolito.rdn'] = 'Dude'
        query['mongolito.path'] = '/^dc=com,dc=example/'
        #query['mongolito.path'] = 'dc=com,dc=example'

        base, filt = reader.convert_query(query)

        self.assertEqual(base, 'dc=example,dc=com')
        self.assertEqual(filt, '(&(|(objectClass=userProxyFull)(objectClass=user))(|(cn=Dude)(uid=Dude)(ou=Dude))(description=Hello*))')


if __name__ == "__main__":
    unittest.main()
