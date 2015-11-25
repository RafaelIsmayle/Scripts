#!/bin/bash
#
# Última alteração 09/06/2014 por Dyego M. Bezerra
# Script para realização/replicacao de backup
#
# Este script deve ser executado com o usuário "PLONE"


ploneCluster=("servidor1" "servidor2" "servidor3")
export ipZeoServer="192.168.0.100"

# Definição de caminhos
export localBackup="/var/Plone/versao4/backups"
export localDataFs="/opt/Plone-4/zeocluster/var/filestorage/Data.fs"
export binRepozo="/opt/Plone-4/zeocluster/bin/repozo"
export binariosZeoPlone="/opt/Plone-4/zeocluster/bin"
#export localBlobStorage="/opt/Plone-4/zeocluster/var/blobstorage/"
export ultiZeoTxt="/var/Plone/ultimoZeo"

ultimoZeo="$(cat $ultiZeoTxt)"

if [ $USER != "plone" ]; then
	echo 'ERRO: execução com usuário incorreto'
	exit 1
fi

telaInicial()
{
	clear
	echo "    Administracao do Servidor Zeo - Zope - Plone 4"
	echo "    ********************************************"
	echo -e "\n    1 - Verificar serviços"
	echo "    2 - Subir ultimo cluster"
	echo "       ($ultimoZeo como ZeoServer e clientes em ${ploneCluster[*]} )"
	echo "    3 - Parar serviços"
	echo "       (novas opções serão exibidas)"
	echo "    4 - Reiniciar instâncias"
	echo "       (todas)"
	echo -e "\n    X - Alterar ZeoServer \n"
	echo -e "    S - Sair\n"
	echo -n "    Digite a opção desejada: "
	read escolha
	case $escolha in
		1) clear; verificaServicos ; echo -e "\n pressione enter para continuar...";read;telaInicial;;
		2) clear; subirUltimo; echo -e "\n pressione enter para continuar...";read;telaInicial;;
		3) clear; pararServicos ; echo -e "\n pressione enter para continuar...";read;telaInicial;;
		4) clear; reiniciarClients; echo -e "\n pressione enter para continuar...";read;telaInicial;;
		X|x) opcoesZeo ;echo -e "\n Pressione enter para continuar...";read;telaInicial;;
		s|S) clear;exit;;
		*) telaInicial;;
	esac
}

backupFull()
{
	echo "Realizando backup, aguarde..."
	ssh $zeoAtual "$binRepozo -vBFz -f $localDataFs -r $localBackup"
	
	for i in ${ploneCluster[*]}; do
		if [ $i == $zeoAtual ]; then 
			continue
		fi
		export no="$i"
		
		echo -e "\n`date '+%d/%m/%Y %T'` - Replicação do backup em $i"
		rsync -vrlptg $localBackup/* $no:$localBackup
		
		echo -e "\n`date '+%d/%m/%Y %T'` - Inicio da restauração em $i"
		
		echo "Iniciando restauração do Datafs"
		ssh $i "$binRepozo -vR --date=$ultimoBkp -o $localDataFs -r $localBackup"
	done
	
	echo -e "\nBackup finalizado, pressione Enter para continuar..."; read
}

baixarInterfazeZeo()
{
	for i in {1..3}; do
		echo "Tentativa $i de baixar interface $ipZeoServer."
		ssh $ipZeoServer "sudo /sbin/ifconfig eth0\:1 down"
		
		$(/bin/ping -c 2 $ipZeoServer 2>&1 > /dev/null)
		if [ $? == 1 ]; then
			break
		elif [ $? != 1 ] & [ $i == 3 ]; then
			echo "IP $ipZeoServer continua a responder, favor verificar."
			exit 1
		fi
	done
}


opcoesZeo()
{
	clear
	export ultimoBkp="$(ls -1 $localBackup | egrep -i "\.fs.*$" | sort | tail -1 | cut -d"." -f1)"
	echo "    Alteração de servidor Zeo"
	echo "    ********************************************"
	echo "    Último backup encontrado foi de $(echo $ultimoBkp | awk 'BEGIN {FS="-"};{hora=$4-3; print $3"/"$2"/"$1" às UTC "$4"h"$5"min"}')"
	echo -e "\n    1 - Realizar novo backup e subir em outro nó do cluster"
	echo "    2 - Parar ZeoServer atual e subir em outro nó"
	echo "    3 - Sair"
	echo -ne "\n    Digite a opção desejada: "; read opcaoZeo
	case $opcaoZeo in
		1) clear;alterarZeo "backup";;
		2) clear;alterarZeo;;
		3) clear;exit;;
	esac
	
}

alterarZeo()
{
	ploneNoAr=1
	/bin/ping -c 2 $ipZeoServer > /dev/null || ploneNoAr=0
	
	if [ $1 == "backup" ]; then
	
		if [ $ploneNoAr == "1" ] ; then
			backupFull
		else
			echo "Não foi possível conectar ao ZeoServer ($ipZeoServer)"
			echo -n "Prosseguir para subir serviço do ZeoServer sem realizar novo backup? (s/n): "; read continuar
				case $continuar in
					s|S) ;;
					*) opcoesZeo;;
				esac
		fi
	fi
	
	clear
	echo "    Servidor Zeo"
	echo "    ********************************************"
	echo -e "    Qual deve ser o novo servidor Zeo?\n"
	
	numNoZeo=0
	for i in ${ploneCluster[*]}; do
		echo "    $numNoZeo - $i"
		((numNoZeo++))
	done
	
	echo -ne "\n    Escolha o servidor: "; read novoZeoServer
	case $novoZeoServer in
		[0-$numNoZeo]) ;;
		*) echo "Opção inválida."; sleep 2; opcoesZeo;;
	esac
	
	if [ $ploneNoAr == 1 ];then 
		zeoAtual=$(ssh $ipZeoServer "hostname")
		echo -e "\n Parando serviços em $zeoAtual"
		ssh $zeoAtual "$binariosZeoPlone/plonectl stop"
		echo " Baixando interface eth0:1"
		baixarInterfazeZeo
	fi
	
	echo " Subindo IP do ZeoServer em ${ploneCluster[$novoZeoServer]}"
	subirInterfZeoServer ${ploneCluster[$novoZeoServer]}

	echo " Iniciando ZeoServer em ${ploneCluster[$novoZeoServer]}"
	ssh ${ploneCluster[$novoZeoServer]} "$binariosZeoPlone/zeoserver start"

	reiniciarClients
	
	renovarSshKeys
	
}

subirInterfZeoServer()
{
	$(/bin/ping -c 2 $ipZeoServer 2>&1 > /dev/null)
	if [ $? == 0 ]; then
		echo -n "O IP do ZeoServer ($ipZeoServer) já está em uso, tem certeza que deseja ativá-lo também em $1? (s/n): "; read respostaIP
		case $respostaIP in
			s|S) ;;
			*) echo "Operação abortada."; sleep 2; exit 1;;
		esac
	fi
	
	for i in {1..5}; do
		echo "Tentativa $i de subir interface ZeoServer"
		ssh $1 "sudo /sbin/ifconfig eth0\:1 $ipZeoServer netmask 255.255.252.0"
		
		$(/bin/ping -c 2 $ipZeoServer 2>&1 > /dev/null)
		if [ $? == 0 ]; then
			echo "Resposta de $ipZeoServer OK."
			break
		elif [ $? != 0 ] & [ $i == 5 ]; then
			echo "Não foi possível subir interface $ipZeoServer , favor verificar!"
			sleep 3 ; exit 1
		fi
	done
}

renovarSshKeys()
{
	for i in ${ploneCluster[*]}; do
		ssh $i "sed \"s/$ipZeoServer\ *//g\" -i /home/plone/.ssh/known_hosts"
		echo "Renovando host fingerprint para ZeoServer em $i"
		ssh $i "ssh -o \"StrictHostKeyChecking no\" $ipZeoServer \"echo $HOSTNAME: Revalidação com sucesso\" || echo \"$HOSTNAME: ERRO AO REVALIDAR FINGERPRINT !!!\""
	done
}

reiniciarClients()
{
	for i in ${ploneCluster[*]}; do
		echo -e "\nReiniciando instâncias em $i"
		ssh $i "find $binariosZeoPlone -iregex \".+client[0-9]\" -printf \"%f: \" -exec {} stop \;"
		ssh $i "find $binariosZeoPlone -iregex \".+client[0-9]\" -printf \"%f: \" -exec {} start \;"
	done
}

verificaServicos()
{
	echo -e "\n\n"
	
	$(/bin/ping -c 2 $ipZeoServer 2>&1 > /dev/null)
	if [ $? != 1 ]; then
		echo "IP do ZeoServer ($ipZeoServer) respondeu, verificando origem..."
		zeoAtual="$(ssh $ipZeoServer hostname)"
	
		if [ "$zeoAtual" != "$ultimoZeo" ]; then
			echo "ALERTA,  ZeoServer foi alterado desde o último backup ($ultimoZeo) !!!"
		fi
	
		echo -e "   IP ZeoServer em $zeoAtual"
	else
		echo "ATENÇÃO! IP do ZeoServer ($ipZeoServer) não está respondendo, favor verificar!"
	fi
	
	for i in ${ploneCluster[*]}; do
		echo -e "\n\nServiços em $i =============================\n"
		echo -n "   Estado do ZeoServer em $i: "
		ssh $i "$binariosZeoPlone/zeoserver status"
		echo -e "\n   Estado dos clientes em $i"
		ssh $i "find $binariosZeoPlone -iregex \".+client[0-9]\" -printf \"%f: \" -exec {} status \;"
		
	done
	
}

paraTotalPlone()
{
	for i in ${ploneCluster[*]}; do
		echo -e "\n\nParando serviços em $i: "
		ssh $i "$binariosZeoPlone/plonectl stop"
	done
	
	echo -e "\n\n\nBaixando Interface eth0:1 de $zeoAtual"
	baixarInterfazeZeo
}

pararServicos()
{
	echo "    Parar serviços Plone"
	echo "    ********************************************"
	echo -e "    Parar serviços em:\n"
	
	numNoZeo=0
	for i in ${ploneCluster[*]}; do
		echo "    $numNoZeo - $i"
		((numNoZeo++))
	done
	
	echo -e "\n    V - Para voltar."
	echo -e "\n    X - Para todos os nós do cluster Zeo\n"
	echo -n "Digite a opção desejada: "; read pararNoh
	echo -e "\n"
	
	case $pararNoh in
		[0-$numNoZeo]) echo "Parando serviço em ${ploneCluster[$pararNoh]}"; pararNohCluster ${ploneCluster[$pararNoh]};;
		x|X) paraTotalPlone;;
	esac
}

pararNohCluster()
{
	if [ $zeoAtual == $1 ]; then
		echo "Tem certeza que deseja para o ZeoServer ($1)? (s/n): "; read resposta
		case $resposta in
			s|S) ssh $1 "$binariosZeoPlone/plonectl stop"; baixarInterfazeZeo ;;
			*) echo "Operação abortada."; sleep 2;;
		esac
	else
		ssh $1 "$binariosZeoPlone/plonectl stop"
	fi
}

subirUltimo()
{
	$(/bin/ping -c 2 $ipZeoServer 2>&1 > /dev/null) 
	
	if [ $? == 0 ]; then
		echo -en "ATENÇÃO! IP do ZeoServer está ativo, deseja tentar desativar? (s/n): "
		read respIp
		case $respIp in
			s|S) baixarInterfazeZeo;;
		esac
	fi
	
	echo " Subindo IP do ZeoServer em $ultimoZeo"
	subirInterfZeoServer $ultimoZeo
	echo " Iniciando ZeoServer em $ultimoZeo"
	ssh $ultimoZeo "$binariosZeoPlone/zeoserver start"
	
	reiniciarClients
}


$(/bin/ping -c 1 $ipZeoServer 2>&1 > /dev/null)
if [ $? == 0 ]; then
	zeoAtual=$(ssh $ipZeoServer "hostname")
else
	zeoAtual="nao respondendo"
fi

telaInicial
