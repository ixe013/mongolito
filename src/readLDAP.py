import ldap

class LDAPReader(ldap.ldapobject.LDAPObject, ldap.resiter.ResultProcessor):

    def __init__(self, url, userdn, password):
        super(LDAPReader, self).__init__(self, url)

        self.set_option(ldap.OPT_REFERRALS, 0)
        self.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
        self.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
        self.set_option(ldap.OPT_X_TLS,ldap.OPT_X_TLS_DEMAND)
        self.set_option(ldap.OPT_X_TLS_DEMAND, True )
        self.set_option(ldap.OPT_DEBUG_LEVEL, 255 )

        self.simple_bind_s(userdn, password)

    def __del__(self):
        self.unbind_s()

    def get_attribute(self, query={}, attribute = 'dn', error=KeyError):
        '''Returns an iterator over a single attribute from a search'''
        for ldapobject in self.search(query, [attribute]):
            try:
                yield ldapobject[attribute]
            except KeyError as ke:
                if error is not None:
                    raise ke

    def search(self, query='(objectClass=*)', attributes=[]):
        '''Thin wrapper over ldap.search and ldap.allresults'''

        msg_id = self.search('ou=Utilisateurs,o=Hydro-Quebec,st=qc,c=ca', ldap.SCOPE_SUBTREE, query)

        for res_type, res_data, res_msgid, res_controls in self.allresults(msg_id):
            for dn, entry in res_data:
                # process dn and entry
                entry['dn'] = dn
                yield entry

