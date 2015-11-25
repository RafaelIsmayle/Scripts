
Write-Host '
ATENÇÃO: este script irá alterar as permissões de AdminSDHolder (de hora em hora
o PDC compara as contas administrativas e redefine de acordo com o AdminSDHolder)"
'

$ArqLog=Read-Host "Salvar log em"



    dsacls "cn=adminsdholder,cn=system,dc=empresa,dc=com" /d '"IMPRENSA\Exchange Trusted Subsystem":WPRP;info' >> $ArqLog
    dsacls "cn=adminsdholder,cn=system,dc=empresa,dc=com" /d '"IMPRENSA\Exchange Trusted Subsystem":WPRP;homephone' >> $ArqLog
    dsacls "cn=adminsdholder,cn=system,dc=empresa,dc=com" /d '"IMPRENSA\Exchange Trusted Subsystem":WPRP;mobile' >> $ArqLog
    dsacls "cn=adminsdholder,cn=system,dc=empresa,dc=com" /d '"IMPRENSA\Exchange Trusted Subsystem":WPRP;pager' >> $ArqLog
    dsacls "cn=adminsdholder,cn=system,dc=empresa,dc=com" /d '"IMPRENSA\Exchange Trusted Subsystem":WPRP;facsimileTelephoneNumber' >> $ArqLog
    dsacls "cn=adminsdholder,cn=system,dc=empresa,dc=com" /d '"IMPRENSA\Exchange Trusted Subsystem":WPRP;manager' >> $ArqLog
    
    
        
    echo "
<==============================================================>
" >> $ArqLog
