from ldap3 import Server, Connection, ALL, NTLM, ALL_ATTRIBUTES
server = Server('192.168.0.153', get_info=ALL)
conn = Connection(server, user="jorgie\\administrator",
                  password="Wme.ae123", auto_bind=True)
print(conn.extend.standard.who_am_i())

conn.search('dc=jorgie,dc=local',
            '(mail=jessa@jeorginallave.online)', attributes=ALL_ATTRIBUTES)

print(conn.response_to_json())
