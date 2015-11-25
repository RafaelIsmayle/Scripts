#! /bin/bash
#
# Última edição em 06/11/2013 por Dyego M. Bezerra

pathZabbixSender="/usr/bin/zabbix_sender"
varServNome=$1
varPath=$2

coleta="$(curl http://$varServNome/$varPath 2> /dev/null)"

# Decrementado em 1, pois a propria coleta é uma conexão
conexoesAtivas="$(echo $coleta | awk '{print $3}')"
((conexoesAtivas-=1))

conexoesAceitas="$(echo $coleta | awk '{print $8}')"
conexoesRespondidas="$(echo $coleta | awk '{print $9}')"
requisicoesRespondidas="$(echo $coleta | awk '{print $10}')"

requisicoesEmLeitura="$(echo $coleta | awk '{print $12}')"
requisicoesEmResposta="$(echo $coleta | awk '{print $14}')"
((requisicoesEmResposta-=1))
conexoesKeepAlive="$(echo $coleta | awk '{print $16}')"

# Retorna o número de conexões ativas
echo $conexoesAtivas

$pathZabbixSender -s $varServNome -k conexoesAceitas -z 127.0.0.1 -o $conexoesAceitas 2>&1 > /dev/null

$pathZabbixSender -s $varServNome -k conexoesRespondidas -z 127.0.0.1 -o $conexoesRespondidas 2>&1 > /dev/null

$pathZabbixSender -s $varServNome -k requisicoesRespondidas -z 127.0.0.1 -o $requisicoesRespondidas 2>&1 > /dev/null

$pathZabbixSender -s $varServNome -k requisicoesEmLeitura -z 127.0.0.1 -o $requisicoesEmLeitura 2>&1 > /dev/null

$pathZabbixSender -s $varServNome -k requisicoesEmResposta -z 127.0.0.1 -o $requisicoesEmResposta 2>&1 > /dev/null

$pathZabbixSender -s $varServNome -k conexoesKeepAlive -z 127.0.0.1 -o $conexoesKeepAlive 2>&1 > /dev/null
