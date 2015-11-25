#add-pssnapin Microsoft.Exchange.Management.PowerShell.E2010
# comando que usei para coletar usuarios: dsquery user "ou=exemplo,dc=empresa,dc=com" -limit 0 > usuariosAD_20120810.txt


Write-Host '
É recomendável alterar a permissão de usuário no Schema.

O arquivo a ser lido deve estar em cada linha conforme exemplo:
"CN=João da Silva,OU=Software,OU=Engenharia,DC=Widget,DC=com"
"CN=Pedro da Silva,OU=Software,OU=Engenharia,DC=Widget,DC=com"
'

#$ErrorActionPreference="SilentlyContinue"
#Stop-Transcript | out-null
#$ErrorActionPreference = "Continue"
$ArqLog=Read-Host "Salvar log em"
#Start-Transcript -path $ArqLog -append

$ArqLocal=Read-Host "Especifique o local do arquivo a ser lido"

#$LISTA=Get-Content $ArqLocal
foreach ($i in `Get-Content $ArqLocal` )
    {
    Write-Host "Redefinindo segurança de "$i
    echo "Redefinindo segurança de "$i ":" >> $ArqLog
    #dsacls $i /resetDefaultDACL >> $ArqLog
    dsacls $i /d '"IMPRENSA\Exchange Trusted Subsystem":WPRP;info' >> $ArqLog
    dsacls $i /d '"IMPRENSA\Exchange Trusted Subsystem":WPRP;homephone' >> $ArqLog
    dsacls $i /d '"IMPRENSA\Exchange Trusted Subsystem":WPRP;mobile' >> $ArqLog
    dsacls $i /d '"IMPRENSA\Exchange Trusted Subsystem":WPRP;pager' >> $ArqLog
    dsacls $i /d '"IMPRENSA\Exchange Trusted Subsystem":WPRP;facsimileTelephoneNumber' >> $ArqLog
    dsacls $i /d '"IMPRENSA\Exchange Trusted Subsystem":WPRP;manager' >> $ArqLog
    
    
        
    echo "
<==============================================================>
" >> $ArqLog
     }

#Stop-Transcript
