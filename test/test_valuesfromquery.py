import re
import unittest

import transformations.valuesfromquery

class ModuleTest(unittest.TestCase):

    def testSetQueryParameter(self):
        ldapobject = {
            'objectClass':'inetOrgPerson',
            'uid':'lion-king',
            'floor':'11',
        }

        query = {
            'objectClass':'user',
            'sAMAccountName':transformations.valuesfromquery.PlaceHolderForGroup(1),
            'info':transformations.valuesfromquery.PlaceHolderForGroup(2),
        }
                          
        regex = '(.*)-(.*)$'

        #We want to change the value of the uid attribute
        renamer = transformations.valuesfromquery.ValuesFromQuery('uid', regex, query, None)

        #Pretend that we found a match while looping through all the 
        #attributes
        pattern = re.compile(regex)
        groups = pattern.match(ldapobject['uid']).groups()

        #Get the query prepared with the paramters
        prepared = renamer.set_query_values(groups)

        #The query should look like this. We replaced the place
        #holders with the values of the regex groups (case-insensitive)
        expected = {
            'objectClass':'user',
            'sAMAccountName':{ '$regex':'lion', '$options':'i' },
            'info':{ '$regex':'king', '$options':'i' },
        }
                          
        self.assertEquals(expected, prepared)


if __name__ == "__main__":
    unittest.main()

