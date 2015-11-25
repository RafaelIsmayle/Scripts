#!/bin/bash
#
# Nome do Script: atualiza_awstats.sh
#
# Autor: Dyego
# Data: 21/09/2015
#
# Descrição: Script para automatização de atualização da base do AWStats
#

localLogs="/mnt/logacesso/"

argParse()
{
if [[ -z $@ ]]; then ajuda; exit 1; fi

getopt_results=`getopt -s bash -o :: --long log:,config:: -- "$@"`

if test $? != 0
then
    ajuda
    exit 1
fi

eval set -- "$getopt_results"

while true
do
    case "$1" in
        --log) siteLog=$2; shift 2 ;;
        --config) siteConfig=$2; shift 2 ;;
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
Utilize as opções --log e --config
Exemplo: atualiza_awstats.sh --log=portal --config=portal.in.gov.br
 """ > /dev/stderr
}

argParse $@

cd "${localLogs}"

for data in `ls -d 2*`
do
	arquivos=$(find $localLogs/$data -type f -name "access_${siteLog}_*" -not -iname '*.gz')
	arquivos=$(echo $arquivos | sed 's/\n/\ /g')
	if [[ ! -z $arquivos ]]; then
		echo "-----------------------------------------------"
		echo -e "Início em: $(date +"%Y/%m/%d %H:%M:%S") \nDiretório: $(pwd) \nAWStats config: ${siteConfig} \n"
		perl /usr/local/awstats/wwwroot/cgi-bin/awstats.pl --config=$siteConfig --update -LogFile="/usr/local/awstats/tools/logresolvemerge.pl ${arquivos} |" 
		gzip ${arquivos}
		echo -e "\nTérmino em: $(date +"%Y/%m/%d %H:%M:%S") \n"
	fi
done
