#!/bin/bash
#
# Nome do Script: jboss-cli_zabbix.sh
#
# Autor: Dyego M. B. - dyegomb.wordpress.com | https://github.com/dyegomb/
# Data: 22/07/2015
#
# Descrição: Script de integração do Zabbix com o jboss-cli
#

pathCli="/opt/jboss-eap-6.4/bin/jboss-cli.sh"
pathZabbixSender="/usr/bin/zabbix_sender"
zabbixServer="127.0.0.1"

argParse()
{
getopt_results=`getopt -s bash -o :: --long executar:,lld:,controller:,host:,server:,ds:,zabbixHost:,user:,pass:,get:,consulta:,complemento:: -- "$@"`

if test $? != 0
then
    echo "Opção não reconhecida."
    exit 1
fi

eval set -- "$getopt_results"

while true
do
    case "$1" in
        --executar) shift ; jbExecutar=$(echo $@ | sed 's/\s\-\-//g' ); break ;;
        --lld) tipoLLD=$(echo $2 | tr [:lower:] [:upper:]); shift 2 ;;
		--controller) jbController=$2; shift 2 ;;
		--host) jbHost=$2; shift 2 ;;
		--server) jbServer=$2; shift 2 ;;
		--ds) jbDatasource=$2; shift 2 ;;
		--zabbixHost) hostZabbixName=$2; shift 2 ;;
		--zabbixServer) zabbixServer=$2; shift 2 ;;
		--user) usuario=$2; shift 2 ;;
		--pass) senha=$2; shift 2 ;;
		--consulta | --get) consultaTipo=$(echo $2 | tr [:lower:] [:upper:]); shift 2 ;;
		--complemento) complementoTipo=$2; shift 2 ;;
        --) shift; break ;;
        *)  echo "$0: opção inválida $1"
            EXCEPTION=$Main__ParameterException
            EXCEPTION_MSG="opção inválida $1"
			ajuda
            exit 1
            ;;
    esac
done
}

ajuda()
{
echo -e """
Script de integração do Zabbix com a ferramenta jboss-cli do JBoss EAP 6 ou JBoss AS 7.

 --lld\t\tRealiza um LLD para Zabbix.
\t\tos valores possíveis são: Servers, DS, SrvGroups.
 --get\t\tRealiza uma consulta e retorna os valores via \"zabbix_sender\".
\t\tos valores possíveis são: ServerMem, DSStats.
 --controller\tInforma o JBoss Domain Controller.
 --host \tInforma o JBoss Host.
 --server\tInforma o JBoss Server.
 --ds\t\tInforma o nome do Datasource do JBoss.
 --zabbixServer\tInforma o IP do servidor Zabbix.
 --zabbixHost\tInforma o nome do Host monitorado pelo Zabbix.
 --user \tUsuário para acesso ao JBoss.
 --pass \tSenha para acesso ao JBoss.
 
 Autor: Dyego M. B. - dyegomb.wordpress.com
 """
}

cliExecutar() 
{ 
saida=$($connJbossCLI --command="${*}")
capFalha=$(echo $saida | grep -i failed)

if [[ ! -z $capFalha ]] || [[ -z $saida ]] ; then
	echo "ERRO: erro ao executar comando: \"$@\" | RESULTADO=\"$capFalha\""
	exit 2
else
	echo $saida
fi

}

decimalHash()
{
# http://stackoverflow.com/a/7265130
local saida=$(md5sum <<< "$@")
saida=$(echo $((0x${saida%% *})))
if [[ $saida -lt 0 ]]; then 
	saida=$(($saida * -1))
fi
echo $saida
}

lldHostEServers()
{
local resultado=$(cliExecutar 'ls host')
if [[ $(echo $resultado | grep ERRO: ) ]] ; then echo $resultado ; exit 3 ; fi

local saida=$lldInicio
for i in $resultado; do
	local resultado2=$(cliExecutar "ls /host=$i/server")
		for a in $resultado2 ; do
			saida=$saida"{ \"{#JBHOST}\":\"$i\", \"{#JBSERVER}\" : \"$a\" },\n"
		done
done
saida="$(echo $saida | rev | cut -c 4- | rev)"
saida=$saida$lldFim
echo -e $saida
}

lldDatasource()
{
local resultado=$(cliExecutar 'ls host')
if [[ $(echo $resultado | grep ERRO: ) ]] ; then echo $resultado ; exit 3 ; fi
local resultado2=""
local resultado3=""
local saida=""

saida=$lldInicio
for iHost in $resultado; do
	resultado2=$(cliExecutar "ls /host=$iHost/server")
	for iServer in $resultado2 ; do
		resultado3=$(cliExecutar "ls /host=$iHost/server=$iServer/subsystem=datasources/data-source")
		for iDS in $resultado3 ; do
			saida=$saida"{ \"{#JBHOST}\":\"$iHost\", \"{#JBSERVER}\" : \"$iServer\", \"{#JBDATASOURCE}\" : \"$iDS\"},\n"
		done
	done
done
saida="$(echo $saida | rev | cut -c 4- | rev)"
saida=$saida$lldFim
echo -e $saida

}

lldDeploys()
{
local resultado=$(cliExecutar 'ls host')
if [[ $(echo $resultado | grep ERRO: ) ]] ; then echo $resultado ; exit 3 ; fi

local saida=$lldInicio
for i in $resultado; do
	local resultado2=$(cliExecutar "ls /host=$i/server")
		for a in $resultado2 ; do
			local resultado3=$(cliExecutar "ls /host=${i}/server=${a}/deployment")
				for b in $resultado3 ; do
					saida=$saida"{ \"{#JBHOST}\":\"$i\", \"{#JBSERVER}\" : \"$a\", \"{#JBDEPLOY}\" : \"$b\" },\n"
					done
		done
done
saida="$(echo $saida | rev | cut -c 4- | rev)"
saida=$saida$lldFim
echo -e $saida
}

trataLsSimples()
{
saida=$lldInicio
nomeValor=$1
shift

if [ $# -lt 1 ]; then 
	echo "ERRO: Não há resultados."; 
	return 10; 
fi

for i in $@; do
	saida=$saida"{ \"{#$nomeValor}\":\"$i\" },\n"
done	
saida="$(echo $saida | rev | cut -c 4- | rev)"
saida=$saida$lldFim
echo -e $saida
}

dsStats()
{
local jbHost=$1 ; shift
local jbServer=$1 ; shift
local datasource=$1

for tipo in pool jdbc ; do
	local comando="ls /host=${jbHost}/server=${jbServer}/subsystem=datasources/data-source=${datasource}/statistics=${tipo}:read-resource(include-runtime=true)"
	local resultado=$(cliExecutar $comando)
	if [[ $(echo $resultado | grep ERRO: ) ]] ; then echo $resultado ; continue ; fi
	if [ "$(echo $resultado | grep -o '"outcome" => "failed"')" = "" ] ; then
		for dado in $resultado; do
			item=$(echo $dado | awk -F'=' '{ print $1 }')
			valor=$(echo $dado | awk -F'=' '{ print $2 }')
			$pathZabbixSender -s $hostZabbixName -k "DsStats[${jbHost}/${jbServer}/${datasource}, ${item}]" -z ${zabbixServer} -o ${valor} 2>&1 > /dev/null
		done
	fi
done
}

srvMem()
{
local jbHost=$1 ; shift
local jbServer=$1 ; shift
local zabbixHost=$1 ; shift
local dados=$@

capFalha=$(echo $dados | grep -i failed)

if [[ ! -z $capFalha ]] ; then
	echo "ERRO: erro ao executar comando: \"$@\" | RESULTADO=\"$capFalha\""
	exit 2
fi

local heapInit=""
local heapUsed=""
local heapComm=""
local heapMax=""
local nHeapInit=""
local nHeapUsed=""
local nHeapComm=""
local nHeapMax=""
local heapDados=""
local nonHeapDados=""

heapDados=$(echo ${dados} | awk -F'[{}]' '{ print $2}')
heapInit=$(echo $heapDados | grep -Po '(?<=\"init" => )[0-9]*(?=L,"used)')
heapUsed=$(echo $heapDados | grep -Po '(?<=\"used" => )[0-9]*(?=L,"committed)')
heapComm=$(echo $heapDados | grep -Po '(?<=\"committed" => )[0-9]*(?=L,"max)')
heapMax=$(echo $heapDados | grep -Po '(?<=\"max" => )[0-9]*(?=L)')

nonHeapDados=$(echo ${dados} | awk -F'[{}]' '{ print $4}')
nonHeapInit=$(echo $nonHeapDados | grep -Po '(?<=\"init" => )[0-9]*(?=L,"used)')
nonHeapUsed=$(echo $nonHeapDados | grep -Po '(?<=\"used" => )[0-9]*(?=L,"committed)')
nonHeapComm=$(echo $nonHeapDados | grep -Po '(?<=\"committed" => )[0-9]*(?=L,"max)')
nonHeapMax=$(echo $nonHeapDados | grep -Po '(?<=\"max" => )[0-9]*(?=L)')

$pathZabbixSender -s $zabbixHost -k "serverMem[${jbHost}/${jbServer}, heapInit]" -z ${zabbixServer} -o $heapInit 2>&1 > /dev/null
$pathZabbixSender -s $zabbixHost -k "serverMem[${jbHost}/${jbServer}, heapUsed]" -z ${zabbixServer} -o $heapUsed 2>&1 > /dev/null
$pathZabbixSender -s $zabbixHost -k "serverMem[${jbHost}/${jbServer}, heapComm]" -z ${zabbixServer} -o $heapComm 2>&1 > /dev/null
$pathZabbixSender -s $zabbixHost -k "serverMem[${jbHost}/${jbServer}, heapMax]" -z ${zabbixServer} -o $heapMax 2>&1 > /dev/null

$pathZabbixSender -s $zabbixHost -k "serverMem[${jbHost}/${jbServer}, nonHeapInit]" -z ${zabbixServer} -o $nonHeapInit 2>&1 > /dev/null
$pathZabbixSender -s $zabbixHost -k "serverMem[${jbHost}/${jbServer}, nonHeapUsed]" -z ${zabbixServer} -o $nonHeapUsed 2>&1 > /dev/null
$pathZabbixSender -s $zabbixHost -k "serverMem[${jbHost}/${jbServer}, nonHeapComm]" -z ${zabbixServer} -o $nonHeapComm 2>&1 > /dev/null
$pathZabbixSender -s $zabbixHost -k "serverMem[${jbHost}/${jbServer}, nonHeapMax]" -z ${zabbixServer} -o $nonHeapMax 2>&1 > /dev/null

}

webConnectorStats()
{
local jbHost=$1 ; shift
local jbServer=$1 ; shift
local jbConnector=$1 ; shift
local zabbixHost=$1 ; shift

local comando="ls /host=${jbHost}/server=${jbServer}/subsystem=web/connector=${jbConnector}:read-resource(include-runtime=true)"
local resultado=$(cliExecutar $comando)
if [[ $(echo $resultado | grep ERRO: ) ]] ; then echo $resultado ; exit 3 ; fi

for i in ${resultado}; do
	if [[ $( echo $i | grep -v '=') ]] ; then continue; fi
	item=$(echo $i | awk -F'=' '{print $1}')
	valor=$(echo $i | awk -F'=' '{print $2}')
	
	if [[ -z $item ]] || [[ -z $valor ]] ; then continue ; fi
	
	$pathZabbixSender -s $zabbixHost -k "webStats[${jbHost}/${jbServer}/connector, ${item}]" -z ${zabbixServer} -o ${valor} 2>&1 > /dev/null
done
}

serverDeploy()
{
local jbHost=$1 ; shift
local jbServer=$1 ; shift
local jbDeploy=$1 ; shift
local zabbixHost=$1 ; shift
local resultado=$@

if [[ $(echo $resultado | grep '\=\[' ) ]] ; then 
	local item=$(echo $resultado | grep -Po '.*(?=\=\[)' | rev | cut -d" " -f 1 | rev)
	# Uma vez que o Zabbix não compara texto, foi necessário gerar apenas números
	local valorTexto=$(echo $resultado | grep -Po '(?<=\[).*(?=\])')
	local valor=$(decimalHash "${valorTexto}")
	$pathZabbixSender -s $zabbixHost -k "serverDeploy[${jbHost}/${jbServer}/${jbDeploy}, ${item}]" -z ${zabbixServer} -o ${valor} 2>&1 > /dev/null
	resultado=$(echo $resultado | sed "s/${item}\=\[${valorTexto}\]//g")
fi

for i in ${resultado}; do
	if [[ $( echo $i | grep -v '=') ]] ; then continue; fi
	local item=$(echo $i | awk -F'=' '{print $1}')
	local valor=$(echo $i | awk -F'=' '{$1 = ""; print $0}')
	if [[ -z $item ]] || [[ -z $valor ]] ; then continue ; fi
	
	$pathZabbixSender -s $zabbixHost -k "serverDeploy[${jbHost}/${jbServer}/${jbDeploy}, ${item}]" -z ${zabbixServer} -o ${valor} 2>&1 > /dev/null
done
}

jbossDeploy()
{
local jbDeploy=$1 ; shift
local zabbixHost=$1 ; shift
local resultado=$@

if [[ $(echo $resultado | grep '\=\[' ) ]] ; then 
	local item=$(echo $resultado | grep -Po '.*(?=\=\[)' | rev | cut -d" " -f 1 | rev)
	# Uma vez que o Zabbix não compara texto, foi necessário gerar apenas números
	local valorTexto=$(echo $resultado | grep -Po '(?<=\[).*(?=\])')	
	local valor=$(decimalHash "${valorTexto}")
	$pathZabbixSender -s $zabbixHost -k "jbossDeploy[${jbDeploy}, ${item}]" -z ${zabbixServer} -o ${valor} 2>&1 > /dev/null
	resultado=$(echo $resultado | sed "s/${item}\=\[${valorTexto}\]//g")
fi

for i in ${resultado}; do
	if [[ $( echo $i | grep -v '=') ]] ; then continue; fi
	local item=$(echo $i | awk -F'=' '{print $1}')
	
	local valor=$(echo $i | awk -F'=' '{$1 = ""; print $0}')
	
	if [[ -z $item ]] || [[ -z $valor ]] ; then continue ; fi
	
	$pathZabbixSender -s $zabbixHost -k "jbossDeploy[${jbDeploy}, ${item}]" -z ${zabbixServer} -o ${valor} 2>&1 > /dev/null
done

}

lldInicio='{ "data": [\n'
lldFim='\n] }'
consultaTipo=""

argParse $@
connJbossCLI="nice -n 10 $pathCli -c --controller=$jbController --user=$usuario --password=$senha"

if [ "$jbExecutar" != "" ] ; then
	cliExecutar $jbExecutar
	exit
	
elif [ ! -z $tipoLLD ]; then
	if [ "$tipoLLD" = "SERVERS" ] ; then
		lldHostEServers
		exit
	
	elif [ "$tipoLLD" = "SRVGROUPS" ] ; then
		comando="ls server-group"
		resultado=$(cliExecutar $comando)
		trataLsSimples JBSRVGROUP ${resultado}
		exit
	
	elif [ "$tipoLLD" = "DS" ] ; then
		lldDatasource ${resultado}
		exit
	elif [ "$tipoLLD" = "DEPLOY" ] ; then
		lldDeploys
		exit
	else
		ajuda
	fi
	
elif [ ! -z $consultaTipo ] ; then
	if [ $consultaTipo = "SERVERMEM" ]; then
		if [ -z $jbHost ] || [ -z $jbServer ] || [ -z $hostZabbixName ] ; then
			echo "ERRO: Para utilizar esta opção é necessário fornecer Host (--host), Servidor (--server) e Host Zabbix (--zabbixHost)."
			exit 20
		fi
		comando="ls /host=${jbHost}/server=${jbServer}/core-service=platform-mbean/type=memory:read-resource(include-runtime=true)"
		resultado=$(cliExecutar $comando)
		if [[ $(echo $resultado | grep ERRO: ) ]] ; then echo $resultado ; exit 3 ; fi
		srvMem ${jbHost} ${jbServer} ${hostZabbixName} ${resultado}
		exit
	elif [ $consultaTipo = "DSSTATS" ]; then
		if [ -z $jbHost ] || [ -z $jbServer ] || [ -z $jbDatasource ] || [ -z $hostZabbixName ]; then
			echo "ERRO: Para utilizar esta opção é necessário fornecer Host (--host), Servidor (--server), Datasource (--ds) e Host Zabbix (--zabbixHost)."
			exit 20
		fi
		dsStats ${jbHost} ${jbServer} ${jbDatasource} ${hostZabbixName}
		exit
	elif [ $consultaTipo = "WEBCONNECTOR" ]; then
		if [[ -z $jbHost ]] || [[ -z $jbServer ]] || [[ -z $hostZabbixName ]] || [[ -z $complementoTipo ]]; then
			echo "ERRO: Para utilizar esta opção é necessário fornecer Host (--host), Servidor (--server), complemento (--complemento) e Host Zabbix (--zabbixHost)."
			exit 20
		fi
		webConnectorStats ${jbHost} ${jbServer} ${complementoTipo} ${hostZabbixName}
	elif [ $consultaTipo = "SERVERDEPLOY" ]; then
		if [[ -z $jbHost ]] || [[ -z $jbServer ]] || [[ -z $hostZabbixName ]] || [[ -z $complementoTipo ]]; then
			echo "ERRO: Para utilizar esta opção é necessário fornecer Host (--host), Servidor (--server), complemento (--complemento) e Host Zabbix (--zabbixHost)."
			exit 20
		fi
		comando="ls /host=${jbHost}/server=${jbServer}/deployment=${complementoTipo}:read-resource(recursive=true,include-runtime=true)"
		resultado=$(cliExecutar $comando)
		
		serverDeploy ${jbHost} ${jbServer} ${complementoTipo} ${hostZabbixName} ${resultado}
	elif [ $consultaTipo = "JBOSSDEPLOY" ]; then
		if [[ -z $hostZabbixName ]] || [[ -z $complementoTipo ]]; then
			echo "ERRO: Para utilizar esta opção é necessário fornecer complemento (--complemento) e Host Zabbix (--zabbixHost)."
			exit 20
		fi
		comando="ls deployment=${complementoTipo}"
		resultado=$(cliExecutar $comando)
		
		jbossDeploy ${complementoTipo} ${hostZabbixName} ${resultado}
	else
		ajuda
	fi
else
	ajuda
fi
