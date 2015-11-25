#!/usr/bin/env python3
#
# Relaciona relatorios enviados com colaboradores
#
# Última alteração em 21/02/2014 por Dyego M. Bezerra
#
import os,  calendar, time, zipfile, sys, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import parseaddr, formataddr


sys.path.append('.')
from coleta_relatorios import gerenciasTI, compactaArquivos, localRelatorios, listaMeses, calculaOntem, emailPreposto, dadosEmail

destinatarios=[emailPreposto]
localDir=os.getcwd()
localLogVErro=os.path.abspath(localDir+"\\log\\logVerifLogErro.txt")
localLogVOut=os.path.abspath(localDir+"\\log\\logVerifLog.txt")


# o script irá procurar por ao menos 3 operadores por dia
operadores={'OPERADOR1',
            'OPERADOR2',
            'OPERADOR3'}
            
weekWorkers={
'GERENCIA1':{'TRABALHADOR1', 
         'TRABALHADOR2'},

'GERENCIA2':{'TRABALHADOR3', 
	 'TRABALHADOR4'},

'GERENCIA3':{'TRABALHADOR5'}
}

dadosEmailVerifi={
'destinatarios':destinatarios,
'contaEnvio':str(dadosEmail['contaEnvio']),  # Conta de email utilizada para envio
'contaResposta':str(dadosEmail['contaResposta']), # Conta de email utilizada para resposta
'servidor':str(dadosEmail['servidor']), # Servidor SMTP
'portaSMTP':dadosEmail['portaSMTP'],
'usuario':str(dadosEmail['usuario']), # str(dadosEmail['usuario'] Usuário para autenticação SMTP (não necessário atualmente)
'senha':str(dadosEmail['senha']), # str(dadosEmail['senha'] Senha para autenticação SMTP (não necessário atualmente)
} 

        
def confereMesAnterior(anoHoje, mesHoje, excluirOrig=True, mesAtual=False):
    """Confere se o relatório já está compactado e exclui a pasta do mes"""
    
    if not mesAtual:
        anoMesPassadoNum=calculaOntem(anoHoje, mesHoje, 1)[:2]
    elif mesAtual:
        anoMesPassadoNum=[anoHoje, mesHoje]
    
    mesPassadoStr=listaMeses[int(anoMesPassadoNum[1]-1)]
    mesPassadoPath=str(anoMesPassadoNum[1]).rjust(2, '0')+' '+mesPassadoStr
    
    ultDia=calendar.monthrange(anoMesPassadoNum[0], anoMesPassadoNum[1])[1]
    os.chdir(localRelatorios)
    
    for gerencia in gerenciasTI:
        os.chdir(localRelatorios)
        localAno=localRelatorios+'\\'+gerencia+'\\'+str(anoMesPassadoNum[0])
        os.chdir(localAno)
        
        if os.path.exists(mesPassadoPath):
            localMes=localAno+'\\'+mesPassadoPath
            os.chdir(localMes)
            
            for diaNum in range(1, int(ultDia+1)):
                strDia=str(diaNum).rjust(2, '0')
                localDia=localMes+'\\'+strDia
                if os.path.exists(strDia): 
                    nomeZipArq=localMes+'\\'+str(anoMesPassadoNum[0])+str(anoMesPassadoNum[1]).rjust(2, '0')+strDia+'-RDA.zip'
                    compactaArquivos(localDia, nomeZipArq, delArquivos=excluirOrig, filtroArquivos=['*.xls', '*.xlsx'])
                    os.chdir(localMes)
                    
                os.chdir(localMes)
            
            if excluirOrig:
                nomeZipMes=localAno+'\\'+str(anoMesPassadoNum[0])+str(anoMesPassadoNum[1]).rjust(2, '0')+'-'+gerencia+'-RDA.zip'
                compactaArquivos(localMes, nomeZipMes, delArquivos=True, filtroArquivos=['*.zip'])
   

def send_email(recipients=["email@recebe.com"],subject="Assunto",
               body="Corpo",server="bianca", port=587, 
               sender="Sender <email@envia.com>",replyto="Sender <email@envia.com>", 
               username='', password=''): 
    """Sends an e-mail"""

    charset='UTF-8'
    to = ",".join(recipients)

    try:
        body.encode(charset)
    except UnicodeEncodeError:
        print("Não foi possível codificar " + body + " em " + charset + ".")
        listRetorno=[False, "### ERRO: Não foi possível codificar " + body + " em " + charset ]
        return listRetorno

    msg = MIMEText(body.encode(charset), 'plain', charset)
    msg.set_charset(charset)
    msg['From'] = sender
    msg['To'] = to
    msg['Subject'] = Header(subject, charset)
    
    
    print('Conectando ao servidor ', server)
    mailServer = smtplib.SMTP(server, port)
    mailServer.ehlo()
    if port==587:
        print('Iniciando criptografia')
        mailServer.starttls()
        mailServer.ehlo()
    mailServer.login(username, password)
    try:
        mailServer.sendmail(sender, recipients, msg.as_string())
        print('E-mail enviado.')
    except Exception as Erro:
        print('Erro ao enviar e-mail: '+ str(Erro))
        listRetorno=[False, str(Erro)]
    mailServer.quit()

    
    listRetorno=[True, 'E-mail enviado.']
    return listRetorno

def verifEnvio(anoHoje, mesHoje, diaHoje,  env_email=True,  retornoStr=False, verificOntem=True):
    
    if verificOntem:
        listaOntem=calculaOntem(anoHoje, mesHoje, diaHoje)
    else:
        listaOntem=[anoHoje, mesHoje, diaHoje]
        
    mensagemEmail=str()
    parsedOperador=False
    
#    todosOK=True
    
    for gerencia in gerenciasTI:
        os.chdir(localRelatorios+'/'+gerencia)
        
        os.chdir(str(listaOntem[0]))
        
        mesPastaOntem=str(listaOntem[1]).rjust(2, '0')+' '+listaMeses[int(listaOntem[1]-1)]
        
        os.chdir(mesPastaOntem)
#        print(os.getcwd())
        
        if verificOntem:
            arquivoZipNome=calculaOntem(anoHoje, mesHoje, diaHoje, False)+'-RDA.zip'
        else:
            arquivoZipNome=str(anoHoje)+str(mesHoje).rjust(2, '0')+str(diaHoje).rjust(2, '0')+'-RDA.zip'

        if gerencia == 'GERENCIA1':
            operadorEntregou=set()
            parsedOperador=True
        
        if os.path.exists(arquivoZipNome):
            mensagemEmail+='\n'+gerencia+' - RDA não entregue:\n'
            arquivoZip=zipfile.ZipFile(arquivoZipNome, 'r', 8)
            listaRelatorios=arquivoZip.namelist()
            
            listaEntregou=set()
            
            for nomeRelatorio in listaRelatorios:
                try: 
                    nomeWorkerOK=str(os.path.splitext((nomeRelatorio.split('-')[2]))[0].upper()).replace('_', ' ')
                except Exception:
                    mensagemEmail+='\nArquivo com nome inválido: '+nomeRelatorio+'\n'
#                    print(nomeRelatorio)
#                    todosOK=False
                    
                while nomeWorkerOK.startswith(' '):
                    nomeWorkerOK=nomeWorkerOK[1:]
                
                listaEntregou.add(nomeWorkerOK)
                
                if nomeWorkerOK in operadores:
                    operadorEntregou.add(nomeWorkerOK)
                    parsedOperador=True
            
            naoEntregou=sorted(weekWorkers[gerencia].difference(listaEntregou))
            
            if parsedOperador:
                if len(operadorEntregou) < 1:
                    mensagemEmail+='NÃO HÁ RELATÓRIO DOS OPERADORES.\n'
#                    todosOK=False
                elif len(operadorEntregou) < 4:
                    mensagemEmail+='Nem todos os operadores entregaram relatório, apenas '+', '.join(operadorEntregou)+' entregou(aram).\n'
#                    todosOK=False
                
                parsedOperador=False
            
            if calendar.weekday(listaOntem[0], listaOntem[1], listaOntem[2]) < 5:
#                print('week day', calendar.weekday(anoHoje, mesHoje, diaHoje))
                for i in naoEntregou:
                    mensagemEmail+=i+'\n'
#                    todosOK=False
#            print(sorted(weekWorkers[gerencia].difference(listaEntregou)))
            arquivoZip.close()
        
        else:
            if calendar.weekday(listaOntem[0], listaOntem[1], listaOntem[2]) < 5:
                mensagemEmail+='\nNENHUM relatório da ' + gerencia+' foi entregue\n'
#                todosOK=False
            else:
                mensagemEmail+='\nNão há relatórios para '+ gerencia+'\n'
        #print(mensagemEmail)
        
##    if not todosOK:
    if env_email:
        send_email(recipients=dadosEmailVerifi['destinatarios'],
               subject="RDA não entregue no dia "+str(listaOntem[2])+
                  '/'+str(listaOntem[1])+'/'+str(listaOntem[0]),
               body=mensagemEmail,
               server=dadosEmailVerifi['servidor'],
               port=dadosEmailVerifi['portaSMTP'],
               sender=dadosEmailVerifi['contaEnvio'],
               replyto=dadosEmailVerifi['contaResposta'],
               username=dadosEmailVerifi['usuario'],
               password=dadosEmailVerifi['senha'])
        
    if not retornoStr:
        print("RDA não entregue no dia "+str(listaOntem[2])+
                  '/'+str(listaOntem[1])+'/'+str(listaOntem[0]))
        print(mensagemEmail)
    else:
        print(str("RDA não entregue no dia "+str(listaOntem[2])+
                  '/'+str(listaOntem[1])+'/'+str(listaOntem[0])+'\n'+mensagemEmail))
        return(str("RDA não entregue no dia "+str(listaOntem[2])+
                  '/'+str(listaOntem[1])+'/'+str(listaOntem[0])+'\n'+mensagemEmail))
    
# Captura data do computador
hojeAno=time.localtime()[0]
hojeMes=time.localtime()[1]
hojeDia=time.localtime()[2]


if __name__ == "__main__":
    sys.stdout=open(localLogVOut, 'a')
    sys.stderr=open(localLogVErro,'w')
    print("================== Execução em "+str(hojeDia)+'/'+str(hojeMes)+'/'+str(hojeAno))
    verifEnvio(hojeAno, hojeMes, hojeDia)
    if hojeDia == 15:
        confereMesAnterior(hojeAno, hojeMes)
        print('Realizada compactação e exclusão da pasta do mês anterior.')
    sys.stdout.close()
    sys.stderr.close()

