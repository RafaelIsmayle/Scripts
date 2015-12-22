#!/usr/bin/env python3
#
# Nome do Script: auto_snap
#
# Autor: Dyego M. B. - dyegomb.wordpress.com
# Data: 22/12/2015
#
# Descrição: Script integrado com API do RHEV para automação
#            de snapshots de VMs
#
import http.client, ssl, sys, os, datetime
from base64 import b64encode
from time import sleep
import xml.etree.ElementTree as etree

##------------------- Variáveis a serem definidas -----------------------

servidor="localhost"
portaHTTPS=443
usuario="user@empresa.com
senha="$enh@"
textoSnapDesc="Snapshot realizado automaticamente por script via API."

##------------------- Constantes -----------------------

separador='='*25
cred=usuario+":"+senha
credenciais=b64encode(bytearray(cred,"utf-8")).decode("ascii")
context=ssl.SSLContext(ssl.PROTOCOL_TLSv1)
context.verify_mode=ssl.CERT_NONE
global conexao, headers, timeOut
timeOut=60 #valor em minutos (60=1 hora)
headers={ 'Authorization' : str('Basic '+credenciais),
          'Accept' : "application/xml",
          'Content-type':'application/xml'}
conexao=http.client.HTTPSConnection(servidor, context=context,port=portaHTTPS)



##------------------- FUNÇÕES -----------------------

def api_get(url,tipoResp='xml',headers=headers):
    try:
        conexao.request("GET", url, headers=headers)
        resposta=conexao.getresponse()
        if resposta.code == 200:
            try:
                if tipoResp=='tree':
                    tree=etree.parse(resposta)
                    resposta=tree
                elif tipoResp=='xml':
                    tree=etree.parse(resposta)
                    resposta=tree.getroot()
            except Exception as xmlerro:
                print('ERRO: ao coletar dados XML durante consulta. |',xmlerro)
        elif resposta.code == 404 or resposta.code == 401:
            raise ConnectionError(404)
        else:
            print("ERRO: falha ao tentar conexão, código",resposta.code,", verifique a url:", url)
            raise Exception(str(resposta.code))
            
        return resposta
    except ConnectionError as erro:
        raise ConnectionError(str(erro))
    except Exception as erro:
        print("ERRO: falha ao tentar conexão, verifique o RHEV-M e credenciais.")
        raise RuntimeError(str(erro))

def api_post(url,metodo='POST',corpo=None,respTipo="xml",headers=headers):
    try:
        conexao.request(metodo, url, body=corpo, headers=headers)
        resposta=conexao.getresponse()
        try:
            if respTipo=="tree":
                tree=etree.parse(resposta)
                resposta=tree
            elif respTipo=="xml":
                tree=etree.parse(resposta)
                resposta=tree.getroot()
        except Exception as xmlerro:
            print('ERRO: ao coletar dados XML durante ',metodo,'. |',xmlerro)
            
        return resposta
    except Exception as erro:
        print("ERRO: falha ao tentar conexão, verifique o RHEV-M, credenciais e url:",url)
        

def buscaVM(nomeVM,xmlTree=False):
    """Retorna dict com o ID e uri do Snapshot de backup"""
    
    try:
        resultado=api_get(str('/api/vms?search='+nomeVM),False)
        tree=etree.parse(resultado)
        raiz=tree.getroot()
        if len(raiz)>1: raise Exception('ERRO: Mais de uma VM encontrada.\n')
        resultado=dict()
        for i in raiz:
            resultado.update(i.attrib)
        if resultado=={}: raise Exception('ERRO: VM não encontrada.\n')
        if xmlTree==True: resultado=tree
        return resultado
    except Exception as erro:
        return str(erro)
        raise RuntimeError (erro)

def criarSnap(vmHref,snapDesc):
    """Realiza o snapshot de uma VM."""
    try:
        vmXML=api_get(vmHref)
        print('A realizar snapshot de',vmXML.find('name').text)
        corpoDsc=str("<snapshot><description>"+snapDesc+"</description></snapshot>")
        snapPost=api_post(str(vmHref+'/snapshots'),corpo=corpoDsc)
        
        contador=0
        while True:
            try:
                snapCriado=api_get(snapPost.get('href'))
                snapStatus=str(snapCriado.find('snapshot_status').text).upper()
                contador+=1
                if snapStatus != 'OK':
                    print('aguardando término do snapshot.')
                    sleep(30)
                if int(contador/2) > timeOut:
                    print('TimeOut execido, favor verificar.')
                    break
                    #quit (10)
                else:
                    print('Concluído')
                    break
            except Exception as erro:
                print(erro)
                break

    except Exception as erro:
        raise RuntimeError (erro)


def excluiSnapAnt(vmHref,numDias,descAutoSnap):
    """Exclui Snapshots mais antigos que o número de dias informado"""
    dataAgora=datetime.datetime.now()
    try:
        vmXML=api_get(vmHref)
        vmSnaps=api_get(str(vmHref+"/snapshots"))
        for snap in vmSnaps.iter('snapshot'):
            snapType=snap.find('type').text
            snapDesc=snap.find('description').text
            if snapType != 'regular' or snapDesc != descAutoSnap: continue

            snapData=str(snap.find('date').text).split('T')[0]
            snapData=datetime.datetime.strptime(snapData,'%Y-%m-%d')
            deltaData=dataAgora-snapData
            snapHref=snap.get('href')
            if deltaData.days >= numDias:
                print('Iniciando exclusão de snapshot antigo:',snapData.strftime("%Y-%m-%d"))
                deleteSnap=api_post(snapHref,'DELETE')
                #print(deleteSnap)

                contador=0
                while True:
                    try:
                        snapDelete=api_get(snapHref)
                        print(datetime.datetime.strftime(\
                            datetime.datetime.now(),'%H:%M.%S'),\
                            '- aguardando término da exclusão do snapshot.')
                        sleep(30)
                        contador+=1
                        if int(contador/2) > timeOut:
                            print('TimeOut execido, favor verificar.')
                            break
                            #quit (10)
                    except ConnectionError:
                        print("Snapshot",snap.get('id'),"não foi mais encontrado.")
                        break
    except Exception as erro:
        raise RuntimeError(str(erro))
        
    

##------------------- CORPO -----------------------        

if __name__ == '__main__':
    from optparse import OptionParser
    uso="Script para automação de snapshots para RHEV."
    parser = OptionParser(usage=uso)
    parser.add_option("-c","--cluster", help="Realizar snapshot de \
todo o cluster.",default=False, metavar="cluster")
    parser.add_option("-f","--file", help="Realizar snapshot de \
VMs definidas em arquivo.",default=False, metavar="arquivo")
    parser.add_option("-p","--persistencia", help="Dia a serem mantidos\
os Snapshots anteriores.",default=False, metavar="dias")

    options = parser.parse_args()[0]

    if not options.persistencia or (not options.file and not options.cluster) :
        parser.print_help()
        parser.error("A quantidade de dias para persitência dos snapshots \
deve ser informada (-p) e selecionada a origem das VMs (arquivo ou todas de um cluster).")
        
    elif options.file:
        arquivo=open(options.file,'rb')
        for vmLinha in arquivo.readlines():
            print(separador)
            vmNome=vmLinha.strip(b'\n')
            try:
                vmDados=buscaVM(vmNome.decode())
                if type(vmDados) != dict:
                    textoErro = str("ERRO: Não foi possível realizar snapshot de "+\
                              vmNome.decode()+"||"+vmDados)
                    raise RuntimeError(textoErro)
            except Exception as erro1:
                print(erro1)
                continue

            print('Executando procedimentos para', vmNome.decode())
            
            criarSnap(vmDados['href'],textoSnapDesc)
            excluiSnapAnt(vmDados['href'],int(options.persistencia),textoSnapDesc)
        
    elif options.cluster:
        clustersXML=api_get('/api/clusters')
        clusterID=None
        for cluster in clustersXML.findall('cluster'):
            if cluster.find('name').text == options.cluster:
                clusterID=cluster.get('id')
                break
        if clusterID == None:
            print("Cluster \"",options.cluster,"\" não encontrado.")
            quit(1)
        else:
            vmsXML=api_get('/api/vms')
            for vm in vmsXML.findall('vm'):
                for i in vm.iter('cluster'):
                    if i.get('id')==clusterID:
                        print(separador)
                        vmNome=vm.find('name').text
                        print('Executando procedimentos para', vmNome)
                        criarSnap(vm.get('href'),textoSnapDesc)
                        excluiSnapAnt(vm.get('href'),int(options.persistencia),textoSnapDesc)
                        
    else:
        parser.print_help()
