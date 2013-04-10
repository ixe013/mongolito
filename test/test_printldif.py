import unittest

import printldif

class ModuleTest(unittest.TestCase):

    def testPrint(self):
        expectedDict = {
           'dn':'test',
           'first;line':'8',    #Converts to lowercase
           'objectclass':['top', 'user', 'person'],  #Makes an array
           'version':'1',
           'cn':'Hello:World!',
           'description':'R2VzdGlvbiBkZXMgZG9tYWluZXMgZGUgZMOpbMOpZ2F0aW9uLiBOZSBjb250aWVucyBwYXMgZGUgYmFzZXMgZGUgZG9ubsOpZXMu',
           'uniquemember':['cn=orcladmin,cn=users,dc=delegation,dc=qc,dc=ca', 'cn=orcladmin,cn=users,dc=ireq,dc=qc,dc=ca', 'cn=reportsapp,cn=products,cn=oraclecontext,dc=ireq,dc=qc,dc=ca'],
           'enable':'TRUE',
        }

        #printldif.printDictAsLDIF(expectedDict)

    def testRFC2849WrappedOuput(self):
        attribute = 'l'
        value = 'Bonjour a tous mes amis de la Guadeloupe'*7
        print 'YO'
        for l in printldif.RFC2849WrappedOuput(attribute, value):
            self.assertTrue(len(l)<=7, 'Line not wrapped')


if __name__ == "__main__":
    unittest.main()
