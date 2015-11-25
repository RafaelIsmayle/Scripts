#!/bin/bash
#
# Script para realização/replicação de backup
#
# Última alteração em 10/06/2014 por Dyego M. Bezerra
#
# Este script deve ser executado através do usuário "PLONE"

# Cluster do Plone
export ploneVip="192.168.0.100"
ploneCluster=("servidor1" "servidor2" "servidor3")

# Definição de caminhos
export localBackup="/var/Plone/backups"
export localDataFs="/opt/Plone-4/zeocluster/var/filestorage/Data.fs"
export binRepozo="/opt/Plone-4/zeocluster/bin/repozo"
export logBkp="/var/Plone/plone_backup.log"
export ultiZeoTxt="/var/Plone/ultimoZeo"
export PATH=$PATH:/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin

# Teste de usuário
if [ $USER != "plone" ]; then
	echo "ERRO: execução com usuário incorreto. `date`" >> $logBkp
	exit 1
fi

for i in $* ; do
	case $i in
		"Full") opcao="Full";;
		"Quick") opcao="Quick";;
		"Limpar") limpar=true;;
		*) echo "ERRO: opção \"$*\" inválida. `date`" >> $logBkp; exit 2;;
	esac
done

# Captura informação do ZeoServer
export coletaZeoServer="$(ssh $ploneVip hostname || echo \"ERRO: não foi possível estabelecer comunicação com o ZeoServer !!! `date`\" >> $logBkp; exit 3)"


# Testa se ZeoServer está no nó local
if [ "$coletaZeoServer" == "$HOSTNAME" ]; then

	echo "Execução em `date '+%d/%m/%Y %T'` =====================================" >> $logBkp

	if [ $limpar ] && [ $opcao == "Full" ]; then
		rm -f $localBackup/*
		echo "`date '+%d/%m/%Y %T'` - Removendo arquivos de $localBackup" >> $logBkp
	elif [ $limpar ] && [ $opcao != "Full" ]; then
		echo "ERRO: somente é possível realizar a limpeza em conjunto com backup Full. `date`" >> $logBkp
		exit 4
	fi
	
	echo "ZeoServer atual: $HOSTNAME" >> $logBkp
	echo $HOSTNAME > $ultiZeoTxt
	
	if [ $opcao == "Full" ]; then
		
		echo "`date '+%d/%m/%Y %T'` - Início do backup full" >> $logBkp
		$binRepozo -BFz -f $localDataFs -r $localBackup 2>&1 >> $logBkp
		echo "`date '+%d/%m/%Y %T'` - Fim da realização do backup full" >> $logBkp
	
		export ultimoBkp="$(ls -1 $localBackup | sort | tail -1 | cut -d"." -f1)"
		echo "`date '+%d/%m/%Y %T'` - Ultimo backup gerado $ultimoBkp" >> $logBkp
	
		for i in ${ploneCluster[*]}; do
			if [ $i == $HOSTNAME ]; then 
				continue
			fi
			
			echo "`date '+%d/%m/%Y %T'` - Inicio da restauração em $i" >> $logBkp
			ssh $i "$binRepozo -R --date=$ultimoBkp -o $localDataFs -r $localBackup" 2>&1 >> $logBkp

		done
	
	elif [ $opcao == "Quick" ]; then
		
		echo "`date '+%d/%m/%Y %T'` - Início do backup incremental" >> $logBkp
		$binRepozo -BQz -f $localDataFs -r $localBackup 2>&1 >> $logBkp
		echo "`date '+%d/%m/%Y %T'` - Fim da realização do backup incremental" >> $logBkp
		export ultimoBkp="$(ls -1 $localBackup | sort | tail -1 | cut -d"." -f1)"
		echo "`date '+%d/%m/%Y %T'` - Ultimo backup gerado $ultimoBkp" >> $logBkp
		
		for i in ${ploneCluster[*]}; do
			if [ $i == $HOSTNAME ]; then 
				continue
			fi
			
			echo "`date '+%d/%m/%Y %T'` - Inicio da restauração em $i" >> $logBkp
			$(ssh $i "$binRepozo -R --date=$ultimoBkp -o $localDataFs -r $localBackup") 2>&1 >> $logBkp
			
		done
	fi

	echo "===================================== `date '+%d/%m/%Y %T'`" >> $logBkp
else
	echo "`date '+%d/%m/%Y %T'` - ZeoServer em $coletaZeoServer" >> $logBkp
fi
