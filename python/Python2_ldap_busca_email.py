#!/usr/bin/env python2
import ldap
import getpass

servidoresADs = ['servidorldap1','servidorldap2','servidorldap3']

for i in servidoresADs:
    try:
        servidor = 'ldap://%s:389' % i
        ldap_conn = ldap.initialize(servidor)
        ldap_conn.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
        ldap_conn.set_option(ldap.OPT_REFERRALS, 0)
        #ldap_conn.set_option(ldap.OPT_SIZELIMIT, 1000000)
        ldap_conn.simple_bind("usuario@empresa.com", "$enh@")
        break
    except Exception as e:
        print "Nao foi possivel conectar ao servidor %s: %s" % (i,e)
        continue
    
#ldap_conn = ldap.initialize("ldap://servidor.empresa.com:389")
##teste = ldap_conn.whoami_s()
##print teste

baseDN = "dc=in,dc=local"
searchScope = ldap.SCOPE_SUBTREE

pegaAtributos = ['mail'] #use None para todos

filtroBusca = "(&(cn=*)(objectCategory=person)(!(OU=Bloqueados)))"

try:
    ldap_resultado_id = ldap_conn.search(baseDN, searchScope, filtroBusca, pegaAtributos)
    resultado_set = []
    while 1:
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
