#!/usr/bin/env python3
#verifica_enviados.py
# Reconfere mês já compactado.
#
import sys, os,  zipfile,  calendar
#sys.path.append('.')
#from verifica_enviados import gerenciasTI, operadores, weekWorkers

def extraiDataDeNome(nomeArquivo):
    nomeBase=os.path.basename(nomeArquivo)
    nomeBase=os.path.splitext(nomeBase)[0]
    listaBase=nomeBase.split('-')
    data=listaBase[0]
    
    if len(data) == 6:
        anoExtraido=data[:4]
        mesExtraido=data[4:]
        try:
            nomeExtraido=str(nomeBase.split('-')[1]).upper() #UPPER
        except Exception: nomeExtraido=''
        return {'ano':anoExtraido, 'mes':mesExtraido, 'nome':nomeExtraido}
    if len(data) == 8:
        anoExtraido=data[:4]
        mesExtraido=data[4:6]
        diaExtraido=data[6:]
        try:
            nomeExtraido=str(nomeBase.split('-')[2]).upper()
        except Exception: nomeExtraido=''
        return {'ano':anoExtraido, 'mes':mesExtraido, 'dia':diaExtraido, 'nome':nomeExtraido}
        
    else: raise ValueError('Nome inválido de arquivo: '+nomeBase)


def coletaMesCompactado(localMesZip):
    """Retorna em formato dicionário"""
    dadosRetorno=dict()
    
    with zipfile.ZipFile(localMesZip, 'r', 8) as arqMesZip:
        listaArqZipMes=arqMesZip.namelist()
        listaArqZipMes.sort()
        
        # Varre os arquivos, extraindo-os de dentro do arquivo zipado mensal
        for arqNomeDiaZip in listaArqZipMes:
            arqMesZip.extract(arqNomeDiaZip)
            
            
            # Varre os arquivos diários e coleta as informações
            with zipfile.ZipFile(arqNomeDiaZip,  'r', 8) as arqDiaZip:
                listaNomesOk=arqDiaZip.namelist()
                listaNomesOk.sort()
                
                dadosExtraidosDia=extraiDataDeNome(arqNomeDiaZip)
                
                nomesLista=[]
                
                for nomeRelatDiario in listaNomesOk:
                    try:
                        dadosExtraidosNomes=extraiDataDeNome(nomeRelatDiario)
                    except ValueError:
                        dadosExtraidosNomes={'ano':dadosExtraidosDia['ano'], 
                                             'mes':dadosExtraidosDia['mes'], 
                                             'dia':dadosExtraidosDia['dia'],
                                             'nome':"Nome de arquivo incorreto: "+nomeRelatDiario}
                    
                    nomesLista.append(dadosExtraidosNomes['nome'])
                    
                    dadosRetorno.update({str(dadosExtraidosNomes['ano']+
                                             dadosExtraidosNomes['mes']+
                                             dadosExtraidosNomes['dia']) : 
                                                 set(nomesLista[:])})
                                                     
            os.remove(arqNomeDiaZip)
            
    return dadosRetorno
#    print (dadosRetorno)

def main(localArquivoMensal):
    dadosExtraitosArqMes=extraiDataDeNome(localArquivoMensal)
    dadosMesColetados=coletaMesCompactado(localArquivoMensal)
    
        
    
    listaKeys=[]
    
    for chave in dadosMesColetados.keys():
        listaKeys.append(chave)
    listaKeys.sort()
    
    stringSaida=str()
    for dataDia in listaKeys:
        stringSaida+=str("Referente ao dia "+dataDia[6:]+'/'+dataDia[4:6]+'/'+dataDia[:4]+
        ' os seguintes relatórios não foram entregues: \n')
        
        nomesPresentes=dadosMesColetados.get(dataDia, [str('Erro em '+dataDia)])
#        print(nomesPresentes, dataDia, '\n'*2)
        
        naoEntregaramWeek=sorted(weekWorkers[dadosExtraitosArqMes['nome']].difference(nomesPresentes))
        
#        if len(naoEntregaramWeek) > 0:
#            for colaborador in naoEntregaramWeek:
#                stringSaida+=str(colaborador+'\n')
        
        usarTermo=False
        
        if dadosExtraitosArqMes['nome'] == 'GEARE':
            operadorEntregue=set()
            for nomeWorker in nomesPresentes:
                if nomeWorker in operadores:
                    operadorEntregue.add(nomeWorker)
            
            if len(operadorEntregue) < 3:
                stringSaida+=str('Nem todos os operadores entregaram, apenas '+
                             str(len(operadorEntregue))+' entregou(aram).\n')
                usarTermo=True
                
        if calendar.weekday(int(dataDia[:4]), int(dataDia[4:6]), int(dataDia[6:])) > 4:
            stringSaida+="(fim de semana)\n"
        elif naoEntregaramWeek:
            for colaborador in naoEntregaramWeek:
                stringSaida+=str(colaborador+'\n')
        elif usarTermo:
            stringSaida+='(o restante está entregue)\n'
        else:
            stringSaida+='(todos entregues)\n'
        
        stringSaida+='\n'*2
        stringSaida+='='*30
        stringSaida+='\n'
        
        # Salvar em arquivo?
    tipoSaida=input('Deseja salvar em arquivo? (s,n): ').upper()
    if tipoSaida == 'S':
        localSalvar=os.path.abspath(input('Digite o nome e local do arquivo a ser escrito: '))
        with open(localSalvar, 'a') as arqSaida:
            arqSaida.write(stringSaida)
        print('Arquivo salvo em:', localSalvar)
    else: print(stringSaida)
    
#    print(naoEntregaram)
        

if __name__ == "__main__":
    sys.path.append('.')
    from verifica_enviados import operadores, weekWorkers
    global gerenciasTI, operadores, weekWorkers
    
    if len(sys.argv) > 1 :
        print('Analisando', sys.argv[1])
        localArqMes=sys.argv[1]
    else:
        localArqMes=os.path.abspath(input('Insira o caminho completo do arquivo compactado do mês desejado: '))
    
    main(localArqMes)
    
