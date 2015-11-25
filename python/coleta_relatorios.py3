#!/usr/bin/env python3
#
# Cria pastas, coleta relatórios, zipa e envia e-mail
#

import os,  calendar,  time, glob,  zipfile,  sys
from os.path import basename
from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import parseaddr, formataddr
from base64 import encodebytes

localRelatorios=os.path.abspath('\\\\servidor\\local\\Relatorios_RDA')
localDir=os.getcwd()
localLog=os.path.abspath(localDir+"\\log\\log.txt")
localLogErro=os.path.abspath(localDir+"\\log\\logErro.txt")

emailPreposto='preposto@empresa.com'
emailEnvio='sender@empresa.com''

dadosEmail={'destinatarios':[], # Altere o dicionário gerenciasEmails mais abaixo
'assunto':"RDA -",  # Assunto será acrescido de NOME DA GERENCIA - DD/MM/YYYY
'corpo':"""
Seguem anexos os Relatórios Diários de Atividades.
""",
'contaEnvio':"Alerta <"+emailEnvio+">",  # Conta de email utilizada para envio
'contaResposta':"Alerta <"+emailPreposto+">", # Conta de email utilizada para resposta
'servidor':"smtpserver", # Servidor SMTP
'portaSMTP':587,
'usuario':'sender', # Usuário para autenticação SMTP
'senha':'$enh@', # Senha para autenticação SMTP
'arquivosZip':list() } # Este campo não deve ser alterado

gerenciasTI=['GERENCIA1', 'GERENCIA2', 'GERENCIA3'] # Lista com o nome das Gerências

# Adicione à lista de emails para onde deve ser enviado o email para cada gerência, 
# Obs.: Devem estar iguais a gerenciasTI
gerenciasEmails={
'GERENCIA1':['gerente1@empresa.com','gerente2@empresa.com',emailPreposto], 
'GERENCIA2':['gerente1@empresa.com','gerente2@empresa.com',emailPreposto], 
'GERENCIA3':['gerente1@empresa.com','gerente2@empresa.com',emailPreposto]
}

filtroExtArquivos=['*.xls', '*.xlsx']

quantDiasAnteriores=1  # Quantidade de dias anteriores a serem verificados
quantDiasSeguintes=1  # Quantidade de dias seguintes para criação de pastas

listaMeses=['Janeiro', 'Fevereiro', 'Marco',  'Abril',  'Maio',  'Junho',  
        'Julho',  'Agosto',  'Setembro',  'Outubro',  'Novembro',  'Dezembro']

# Captura data do sistema
hojeAno=time.localtime()[0]
hojeMes=time.localtime()[1]
hojeDia=time.localtime()[2]

def criaPastas(diaAtual,  mesAtual, anoAtual, localInicial,  listaNomes,
               gerencias=[], diasSeguint=3):
    
    capDiaAtual=diaAtual
    capMesAtual=mesAtual
    
    os.chdir(localInicial)
    
    for gerencia in gerencias:
        if not os.path.exists(gerencia):
            os.mkdir(gerencia)
            
        os.chdir(os.path.abspath(localInicial+'/'+gerencia))
        
        if not os.path.exists(str(anoAtual)):
            os.mkdir(str(anoAtual))
        
        os.chdir(str(anoAtual))
            
        mesNome=listaNomes[mesAtual-1]
        mesStr=str(mesAtual).rjust(2, '0')
        mesPasta=str(mesStr+' '+mesNome)
        
        if not os.path.exists(str(mesPasta)): os.mkdir(mesPasta)
            
        os.chdir(mesPasta)
        
        ultDiaMes=int(calendar.monthrange(anoAtual, mesAtual)[1])
        
        pastaDia = diaAtual
            
        for addia in range(1, int(diasSeguint+1)):  # Cria pastas para os dias seguintes
            
            if not os.path.exists(str(pastaDia).rjust(2, '0')):
                if pastaDia > ultDiaMes:
                    diaAtual=1
                    if mesAtual < 12: 
                        mesSeg=mesAtual+1
                        mesNome=listaNomes[mesSeg-1]
                        mesStr=str(mesSeg).rjust(2, '0')
                        mesPasta=str(mesStr+' '+mesNome)
                        
                        os.chdir('..\\')
                        
                        if not os.path.exists(str(mesPasta)):  os.mkdir(mesPasta)
                        os.chdir(mesPasta)
                        if not os.path.exists(str('01')): os.mkdir('01')
                        
                    # Feliz Ano Novo!!!
                    if mesAtual == 12:
                        mesSeg=1
                        mesNome=listaNomes[mesSeg-1]
                        mesStr=str(mesSeg).rjust(2, '0')
                        mesPasta=str(mesStr+' '+mesNome)
                        
                        anoSeg=anoAtual+1
                        
                        os.chdir(os.path.abspath(localInicial+'/'+gerencia))
                        if not os.path.exists(str(anoSeg)):  os.mkdir(str(anoSeg))
                        os.chdir(str(anoSeg))
                        if not os.path.exists(str(mesPasta)):  os.mkdir(str(mesPasta))
                        os.chdir(str(mesPasta))
                        if not os.path.exists('01'):  os.mkdir('01')
                        
                        
#                        virouMes=True
                    continue
                os.mkdir(str(pastaDia).rjust(2, '0'))
                
            pastaDia = diaAtual+addia
        
        os.chdir('..\\')
            
        os.chdir('..\\..\\')
        
        diaAtual=capDiaAtual
        mesAtual=capMesAtual
#        virouMes=False
        

def send_email(recipients=["email@recebe.com"],subject="Assunto",
               body="Corpo",zipfiles=[],server="server", port=25, 
               sender="Sender <email@envia.com>",replyto="Sender <email@envia.com>", 
               username='', password=''): 

    """Sends an e-mail"""
    to = ",".join(recipients)
    charset = "utf-8"
    # Testing if body can be encoded with the charset
    try:
        body.encode(charset)
    except UnicodeEncodeError:
        #print("Não foi possível codificar " + body + " em " + charset + ".")
        listRetorno=[False, "### ERRO: Não foi possível codificar " + body + " em " + charset ]
        return listRetorno

    # Split real name (which is optional) and email address parts
    sender_name, sender_addr = parseaddr(sender)
    replyto_name, replyto_addr = parseaddr(replyto)

    sender_name = str(Header(sender_name, charset))
    replyto_name = str(Header(replyto_name, charset))

    # Create the message ('plain' stands for Content-Type: text/plain)
    try:
        msgtext = MIMEText(body.encode(charset), 'plain', charset)
    except TypeError:
        #print("MIMEText fail")
        listRetorno=[False, "### ERRO: MIMEText fail"]
        return listRetorno

    msg = MIMEMultipart()

    msg['From'] = formataddr((sender_name, sender_addr))
    msg['To'] = to #formataddr((recipient_name, recipient_addr))
    msg['Reply-to'] = formataddr((replyto_name, replyto_addr))
    msg['Subject'] = Header(subject, charset)

    msg.attach(msgtext)

    for zipArquiv in zipfiles:
        part = MIMEBase('application', "zip")
        b = open(zipArquiv, "rb").read()
        # Convert from bytes to a base64-encoded ascii string
        bs = encodebytes(b).decode()
        # Add the ascii-string to the payload
        part.set_payload(bs)
        # Tell the e-mail client that we're using base 64
        part.add_header('Content-Transfer-Encoding', 'base64')
        part.add_header('Content-Disposition', 'attachment; filename='+basename(zipArquiv))
        msg.attach(part)

    s = SMTP()
    try:
        s.connect(server, port)
    except:
        listRetorno=[False, "### ERRO: Não foi possível conectar ao servidor: " +
                     str(server)]
        return listRetorno
    
    s.ehlo()
    if port==587:
        s.starttls()
        s.ehlo()
    if username:
        s.login(username, password)
        
    s.sendmail(sender, recipients, msg.as_string())
    s.quit()
    listRetorno=[True, 'E-mail enviado.']
    return listRetorno
    

def compactaArquivos(LocalArquivos, destinoZip, delArquivos=False, filtroArquivos=['*.xls', '*.xlsx']): 
    
    listaArquivos=[]
    listRetorno=[True]
    os.chdir(LocalArquivos)
# Coleta arquivos
    for tipo in filtroArquivos:
        arquivosTipo=glob.glob(tipo)
        for arqFiltrado in arquivosTipo:
            listaArquivos.append(arqFiltrado)
    
    if listaArquivos:
        try:
            arquivoFiltro=''
            
            with zipfile.ZipFile(destinoZip, 'w', 8) as arquivoZip:
                
                for arquivoFiltro in listaArquivos:
                    arquivoZip.write(arquivoFiltro)
                    
        except Exception as erro:
            listRetorno=[False, '### ERRO: ao compactar arquivo '+arquivoFiltro+'. Motivo: '+
                         str(erro)+'.', listaArquivos]
            return listRetorno
    
    strErro=''
    if delArquivos:
        os.chdir(LocalArquivos)
        try:
            arquivo=LocalArquivos
            for arquivo in listaArquivos:
                os.remove(arquivo)
                
            os.chdir('..')
            os.removedirs(LocalArquivos)
            
        except Exception as erro:
            strErro='ERRO: ao remover arquivo ou diretório '+arquivo+'. Motivo: '+str(erro)+'.'
    
    if not strErro and not listaArquivos:
        listRetorno=[False, 'Não há relatórios', listaArquivos]
    elif strErro:
        listRetorno=[True, strErro, listaArquivos]
    else:
        listRetorno=[True,  'Arquivos compactados.', listaArquivos]

    
    return listRetorno



def calculaOntem(anoHoje, mesHoje, diaHoje, retornaLista=True):
    
    try:
        anoOntem=int(anoHoje)
        mesOntem=int(mesHoje)
        diaOntem=int(diaHoje)
        if len(str(anoOntem)) != 4 or len(str(mesOntem)) > 2 or len(str(diaOntem)) > 2:
            raise ValueError
    except Exception:
        return False
    
    if diaHoje > 1:
        diaOntem=diaHoje-1
        
    elif mesHoje == 1:
        anoOntem=anoHoje-1
        mesOntem=12
        diaOntem=31
        
    else:
        mesOntem=mesHoje-1
        diaOntem=int(calendar.monthrange(anoHoje, mesOntem)[1])
    
    if retornaLista:
        ontemLista=[anoOntem, mesOntem, diaOntem]
        return ontemLista
    else:
        return str(str(anoOntem) + str(mesOntem).rjust(2, '0') + str(diaOntem).rjust(2, '0'))

def main():

    # Chama função criaPasta
    criaPastas(hojeDia, hojeMes, hojeAno, localRelatorios, listaMeses,
               gerenciasTI, int(quantDiasSeguintes+1))
    
    for gerencia in gerenciasTI:
        localGerencia = os.path.abspath(str(localRelatorios+'/'+gerencia))
        os.chdir(localGerencia)
        
        # Varre pastas dos dias anteriores especificados pela variável quantDiasAnteriores
        listaDiaAnterior=calculaOntem(hojeAno, hojeMes, hojeDia)
        
        for i in range(quantDiasAnteriores):
            
            localDia=os.path.abspath(localGerencia+'/'+str(listaDiaAnterior[0])+'/'+
                str(listaDiaAnterior[1]).rjust(2, '0')+' '+listaMeses[listaDiaAnterior[1]-1]+'/'+
                str(listaDiaAnterior[2]).rjust(2, '0'))
            
            if os.path.exists(localDia):
                arquivoZip=os.path.abspath(localGerencia+'/'+str(listaDiaAnterior[0])+'/'+
                str(listaDiaAnterior[1]).rjust(2, '0')+' '+listaMeses[listaDiaAnterior[1]-1]+'/'+
                str(listaDiaAnterior[0])+str(listaDiaAnterior[1]).rjust(2, '0')+
                str(listaDiaAnterior[2]).rjust(2, '0')+'-RDA.zip')
                os.chdir(localDia)
    
                # Compacta os arquivos
                retornoZip=compactaArquivos(localDia, arquivoZip, filtroArquivos=filtroExtArquivos)
                
                dataPtBr=str(str(listaDiaAnterior[2]).rjust(2, '0')+'/'+str(listaDiaAnterior[1]).rjust(2, '0')+'/'+
                    str(listaDiaAnterior[0]))
                
                if retornoZip[0]:
                    print('Relatórios de '+gerencia)
                    print(retornoZip[1])
                    
                    # ENVIA E-MAILs
                    if os.path.exists(arquivoZip):
                        emailAssunto=str(dadosEmail['assunto']+' '+gerencia+' - '+dataPtBr)
                        
                        # Chama a função send_email
                        retornoEmail=send_email(recipients=gerenciasEmails[gerencia],subject=emailAssunto,
                            body=dadosEmail['corpo'],zipfiles=[arquivoZip],server=dadosEmail['servidor'],
                            sender=dadosEmail['contaEnvio'],replyto=dadosEmail['contaResposta'], 
                            username=dadosEmail['usuario'], password=dadosEmail['senha'])
                        
                        print(retornoEmail[1])
                    
                else:
                    print(retornoZip[1]+' para '+gerencia+'.\n')
                
            
            listaDiaAnterior=calculaOntem(listaDiaAnterior[0], listaDiaAnterior[1], listaDiaAnterior[2])
    
    print('\n')


if __name__ == "__main__":
    sys.stderr=open(localLogErro,'w')
    sys.stdout=open(localLog, 'a')
    
    print('==============EXECUÇÃO EM '+str(hojeDia).rjust(2, '0')+
     '/'+str(hojeMes).rjust(2, '0')+'/'+str(hojeAno)+'==============\n')

    main()
    sys.stdout.close()
    sys.stderr.close()
