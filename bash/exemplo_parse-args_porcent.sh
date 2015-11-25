#!/bin/bash
#
# Exemplo de Parse de argumentos
#

args=$(getopt -l "origem:,destino:" -o "o:,d:" -n parseCSV -- "$@")
eval set -- "$args"

dest=""

while [ $# -ge 1 ]; do
	case $1 in
		--) shift; break;;
		-d|--destino) dest=$2;shift;shift;;
		-o|--origem) arquiv=$2;shift;shift;;
	esac
done

oldIFS=$IFS
IFS=$'\n'

total="$(wc -l ${arquiv} | cut -d" " -f 1)"
num=0
>&2 echo -en "Iniciando leitura do arquivo"
for i in $(cat $arquiv); do
	col1="$(echo "${i}" | awk -F';' '{print $1}')"
	ehArq="$(echo "${col1}" | egrep ".+\.\w{1,4}$")"
	
	if [ $num == 0 ]; then printf '\r'; printf ' %0.s' {0..29}; fi
	((num++))
	
	percent="$(awk 'BEGIN{ arredond = sprintf("%.3f", "'$num'"/"'$total'"*100) ; print arredond }')" 2> /dev/null
	[ "${dest}" ] && echo -en "\r$percent %" 
	
	if [ "${ehArq}" ]; then
		continue
	fi
	col2="$(echo "${i}" | awk -F';' '{print $2}')"
	col3="$(echo "${i}" | awk -F';' '{print $3}')"
	if [ "${dest}" ]; then
		echo "${col1}"\;"${col2}"\;"${col3}"\; > $dest
	else
		echo "${col1}"\;"${col2}"\;"${col3}"\;
	fi
	
done
echo

IFS=$oldIFS
