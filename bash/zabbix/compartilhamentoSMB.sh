#!/bin/bash
#
#Script desenvolvido por Dyego M. Bezerra <dyegomb@gmail.com>
#
#Configuração para a Discovery Rule: compartilhamentoSMB.sh["{HOST.CONN}", "Disk"]
#Configuração para o Item Key: compartilhamentoSMB.sh["{HOST.CONN}", "-c", "{#SMBSHARE}", "{#SMBTYPE}"]
#

arqAuth=/home/usuario/.authLeitor

if [ ! -r "${arqAuth}" ]; then
  echo "Arquivo $arqAuth não encontrado ou não pode ser lido."
  exit 1
fi

if [ $2 = "-c" ];
then
  argTrat=$(echo "$3" | sed -e 's/\$/\\\$/')
  varShare="$(smbclient --list $1 -A ${arqAuth} -g 2> /dev/null | xargs -I {} echo "\"{}\"\n")"
  teste=$(echo -e "${varShare}" | cut -d "|" -f 2 | egrep "^${argTrat}$" 2> /dev/null)
  if [ -z "${teste}" ]; then
#Retorna 0 caso não encontre nada
	echo "0"
  else 
#Retorna 1 caso o compartilhamento seja encontrado
	echo "1"
  fi
  exit
fi

varShare="$(smbclient --list $1 -A ${arqAuth} -g 2> /dev/null | xargs -I {} echo "\"{}\"\n")"

IFS=$'\n'

echo "{\"data\":["

discoverLista=""
for i in ${varShare}
do
  if test $(echo $i | grep "\"session request to "); then
	continue
  fi
  smbtipo=$(echo $i | cut -d "|" -f 1)
  smbtipo="$(echo $smbtipo | sed 's/\"//g')"

  smbcomp=$(echo $i | cut -d "|" -f 2)
  if [ $smbtipo == $2 ]; then
	discoverLista=$discoverLista"$(echo -n \{ \"\{#SMBSHARE\}\":\"$smbcomp\", \"\{#SMBTYPE}\":\"$smbtipo\" },\\n)"
  fi
done

discoverLista="$(echo $discoverLista | rev | cut -c 4- | rev)"
echo -e $discoverLista
echo "]}"
