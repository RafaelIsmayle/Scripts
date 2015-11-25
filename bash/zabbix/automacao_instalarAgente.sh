#!/bin/bash
#
# Script destinado para a automação do processo de instalação do agente zabbix nos servidores RedHat
#
#

zabbixServer="192.168.0.111,192.168.20.111"
yumServerZabbiz="servidor"
zabbixServerActive="192.168.0.111"

localConfigZabbix="/etc/zabbix/"
arqPidFile="/var/run/zabbix/zabbix_agentd.pid"
arqLogFile="/var/log/zabbix/zabbix_agentd.log"

localConfigYum="/etc/yum.repos.d/"

nomeComputador="$(echo $HOSTNAME | cut -d "." -f 1 | tr '[:lower:]' '[:upper:]')"

function geraZabbixConfig()
{
	if [ -d $1 ]; then
		if [ -w $1 ]; then
			destinoZConfig="$(echo "$1/zabbix_agentd.conf" | sed 's/\/\//\//g')"
		fi
	else
		echo "[ERRO] local de configuração do Zabbix ($1) não foi especificado ou não existe"
		exit 1
	fi
	
	textoZConfig="#\n
#Configuração gerada via script em `date +%D`\n
#\n
\n
PidFile=$arqPidFile \n
LogFile=$arqLogFile \n
LogFileSize=0\n
\n
Server=$zabbixServer\n
ServerActive=$zabbixServerActive\n
\n
Hostname=$nomeComputador\n
\n
Include=`dirname $destinoZConfig`/zabbix_agentd.d/"

	echo -e $textoZConfig > ${destinoZConfig}
}

function geraYumConfig()
{
	if [ -d $1 ]; then
		if [ -w $1 ]; then
			destinoYConfig="$(echo "$1/inzabbix.repo" | sed 's/\/\//\//g')"
		fi
	else
		echo "[ERRO] local para repositório Yum não foi especificado ou não existe"
                exit 1

        fi
	
	textoYConfig="[inzabbix]\nname=Zabbix\nbaseurl=http://$yumServerZabbiz/repo/\$releasever/\$basearch\nenabled=1\ngpgcheck=0"
	echo -e $textoYConfig > $destinoYConfig

}

. /etc/rc.d/init.d/functions
action $"ADICIONANDO CONFIGURAÇÃO DO REPOSITÓRIO AO YUM: " geraYumConfig $localConfigYum


action $"INSTALAÇÃO DO AGENTE ZABBIX ATRAVÉS DO YUM: " $(yum install zabbix-agent --disablerepo=* --enablerepo=inzabbix -y > /dev/null 2>&1)

action $"GERANDO CONFIGURAÇÃO DO AGENTE ZABBIX: " geraZabbixConfig $localConfigZabbix

action $"ADICIONANDO SERVIÇO DO AGENTE NA INICIALIZAÇÃO DO SISTEMA: " $(chkconfig zabbix-agent on > /dev/null 2>&1)

action $"INICIANDO AGENTE ZABBIX: " $(service zabbix-agent start > /dev/null 2>&1)

