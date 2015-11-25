"!/usr/bin/env python2
import ldap
import getpass

servidoresADs = ['serverldap1','serverldap2','serverldap3']

for i in servidoresADs:
    try:
        servidor = 'ldap://%s:389' % i
        ldap_conn = ldap.initialize(servidor)
        ldap_conn.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
        ldap_conn.set_option(ldap.OPT_REFERRALS, 0)
        #ldap_conn.set_option(ldap.OPT_SIZELIMIT, 1000000)
        ldap_conn.simple_bind("usuario@empresa.com", "$enha")
        break
    except Exception as e:
        print "Nao foi possivel conectar ao servidor %s: %s" % (i,e)
        continue
    

##teste = ldap_conn.whoami_s()
##print teste

baseDN = "dc=empresa,dc=com"
searchScope = ldap.SCOPE_SUBTREE

pegaAtributos = ['distinguishedName'] #use None para todos

filtroBusca = "(&(cn=usuario*)(objectClass=user)(objectCategory=person))"

try:
    ldap_resultado_id = ldap_conn.search_ext(baseDN, searchScope, filtroBusca, pegaAtributos)
    resultado_set = []
    while 1: ##Perigo de Loop
        resultado_tipo, resultado_dado = ldap_conn.result(ldap_resultado_id, 0)
        if (resultado_dado == []):
            break
        else:
            if resultado_tipo == ldap.RES_SEARCH_ENTRY:
                resultado_set.append(resultado_dado)
    for i in resultado_set:
        for a in i:
            for b in a:
                print b

except ldap.LDAPError, e:
    print e
