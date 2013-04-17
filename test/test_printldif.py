import unittest

import printldif

class ModuleTest(unittest.TestCase):

    def testPrint(self):
        expectedDict = {
           'dn':'test',
           'description':"J'ai d\xc3\xa9j\xc3\xa0 test\xc3\xa9 \xc3\xa7a et j'ai d\xc3\xa9test\xc3\xa9 \xc3\xa7a",
           'objectclass':['top', 'user', 'person'],  #Makes an array
           'saisons':['printemps', '\xe5\x96\xb6\xe6\xa5\xad\xe9\x83\xa8', 'automne', 'hiver'], 
           'version':'1',
           'cn':'Hello:World!',
           'uniquemember':['cn=orcladmin,cn=users,dc=delegation,dc=qc,dc=ca', 'cn=orcladmin,cn=users,dc=ireq,dc=qc,dc=ca'*10, 'cn=reportsapp,cn=products,cn=oraclecontext,dc=ireq,dc=qc,dc=ca'],
        }

        printldif.printDictAsLDIF(expectedDict)

    def testRFC2849WrappedOuput(self):
        attribute = 'l'
        value = 'Bonjour a tous mes amis de la Guadeloupe'*7

        for l in printldif.RFC2849WrappedOuput(attribute, ':', value):
            self.assertTrue(len(l)<=76, 'Line not wrapped (%d chars, %s)' % (len(l), l))


if __name__ == "__main__":
    unittest.main()
