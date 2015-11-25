#!/usr/bin/env python3

import time

def calcINFOVIA():
    try:
        horaVerao=int(input("Em horário de verão? (digite 1 para sim e 0 para não): "))
    except ValueError:
        horaVerao=0
        
    print("====================================\nInsira os valores de início do período:")
    diaInicio=int(input("Dia de início : "))
    mesInicio=int(input("Mês de início: "))
    anoInicio=int(input("Ano de início (aaaa): "))
    try:
        horaInicio=int(input("Hora de início [0]: "))
    except ValueError:
        horaInicio=0

    cpuTimeInicio=str(time.mktime((anoInicio, mesInicio, diaInicio, horaInicio,
                                   0, 0, 0, 0, horaVerao))).split(".")[0]

    print("====================================\nInsira os valores de fim do período:")
    diaFim=int(input("Dia de término: "))
    try:
        mesFim=int(input("Mês de término ["+str(mesInicio)+"]:"))
    except ValueError:
        mesFim=mesInicio
    try:
        anoFim=int(input("Ano de término ["+str(anoInicio)+"]:"))
    except ValueError:
        anoFim=anoInicio
    try:
        horaFim=int(input("Hora de término [23]: "))
    except ValueError:
        horaFim=23

    cpuTimeFim=str(time.mktime((anoFim, mesFim, diaFim, horaFim,
                                59,0, 0, 0, horaVerao))).split(".")[0]

    print("====================================")
    titulo=str(input(str("Insira o título [IMP_NAC "+str(diaInicio).rjust(2,"0")+"/"+
                             str(mesInicio).rjust(2,"0")+"/"+str(anoInicio)+" - "+
                             str(diaFim).rjust(2,"0")+"/"+str(mesFim).rjust(2,"0")+
                             "/"+str(anoFim)+"]: ")))
    if not titulo:
        titulo=str("IMP_NAC "+str(diaInicio).rjust(2,"0")+"/"+
                             str(mesInicio).rjust(2,"0")+"/"+str(anoInicio)+" - "+
                             str(diaFim).rjust(2,"0")+"/"+str(mesFim).rjust(2,"0")+
                             "/"+str(anoFim))

    endereco=str("https://portalgtic.serpro.gov.br/clientes/IN/grafico?ip=3368472567&amp;"+
    "id_interface=3825&amp;tm_start="+cpuTimeInicio+"&amp;tm_end="+cpuTimeFim+"&amp;"+
    "graph_title="+titulo+"&amp;tipo=UC")
    print("Endereço a ser acessado:\n",endereco,"\n")

repetir=True
while repetir:
    calcINFOVIA()
    questRepetir=input("Repetir operação? (s/n)[s]:").upper()
    if questRepetir == "N":
        break
