#!/bin/bash

#Script desenvolvido por Dyego M. Bezerra <dyegomb@gmail.com>
#
#Configuração no zabbix Key = callTwiddle.sh["{HOST.CONN}", "{$HOMOL_JNPPORT}", "{$TWIDDLE_USER}", "{$TWID_HOMOL_PWD}", "1", "get", "FreePhysicalMemorySize"]
#
#Exemplo para chamar o Twiddle: sudo /opt/jboss-5.1.0.GA/bin/twiddle.sh -s jnp://server:1499 -u usuario -p "pass" get "java.lang:type=OperatingSystem" FreePhysicalMemorySize
#

#defina o local do Twiddle
pathTwiddle="nice sudo /opt/jboss-5.1.0.GA/bin/twiddle.sh"
pathZabbixSender="/usr/bin/zabbix_sender"

destListaDeploys="/tmp/"

hostConn=$1
 shift
jnpPort=$1
 shift
twdUser=$1
 shift
twdPass=$1
 shift

if [ $1 = "1" ]; then
	tipo=1
	tratamento=1
	shift
   elif [ $1 = "DS" ]; then
	tipo=2
	tratamento=1
	shift
	dataSource=$1
	shift
   elif [ $1 = "DISCOVERDS" ]; then
#para consulta com: query "jboss.jca:service=DataSourceBinding,name=*"
	tipo=3
	tratamento=2
	shift
   elif [ $1 = "DISCOVERWAPP" ]; then
#para a consulta: query "jboss.web:type=Manager,*"
	tipo=3
	tratamento=3
	shift
   elif [ $1 = "DISCOVERAPPJ2EE" ]; then
#para consulta com: query "jboss.web:j2eeType=Servlet,name=default,*"
	tipo=3
	tratamento=4
	shift
   elif [ $1 = "0" ]; then
	tipo=1
	tratamento=0
	shift
   elif [ $1 = "DISCOVERDEPLOY" ]; then
#para consulta com: invoke "jboss.system:service=MainDeployer" listDeployedAsString
	tipo=3
	tratamento=5
	shift
	listaInstanciaDeploys=$1
	shift
   elif [ $1 = "CHECKDEPLOYS" ]; then
#complementa consulta com: invoke "jboss.system:service=MainDeployer" listDeployedAsString
	tipo=3
	tratamento=6
	shift
	listaInstanciaDeploys=$1
	shift
	hostZabbixName=$1
	shift
   else
	echo "Especifique o tipo de consulta a ser realizado"
	exit 1
fi

twdArgs=$*

twiddleCMD="timeout 30s ${pathTwiddle} -s jnp://${hostConn}:${jnpPort} -u ${twdUser} -p ${twdPass}"

if [ $tipo = "2" ]; then
        twdArgs="$(echo $twdArgs | sed "s/DSNOMEDS/$dataSource/g")"
	retorno="$($twiddleCMD $twdArgs 2> /dev/null)"

   elif [ $tipo = "3" ]; then
	retorno="$($twiddleCMD $twdArgs | xargs -I {} echo {}\\n 2> /dev/null)"

   else
	retorno="$($twiddleCMD $twdArgs 2> /dev/null)"
fi

if [ $tratamento = "1" ]; then
	echo "$(echo $retorno | cut -d "=" -f 2)"
   elif [ $tratamento = "2" ]; then
	saida="{\"data\":[\\n "
	saida=$saida"$(echo -e $retorno| cut -d '=' -f 3 | xargs -I {} echo { \"{#DSNAME}\":\"{}\" },\\n)"
	saida="$(echo $saida | rev | cut -c 4- | rev)"
	saida=$saida"\\n]}"
	echo -e $saida

   elif [ $tratamento = "3" ]; then
	saida="{\"data\":[\\n"
	for i in $(echo -e $retorno); do
		nomeApp="$(echo $i| egrep -o '\/[a-Z]*+')"
		if [ "$nomeApp" = "/" ]; then
			nomeApp="$(echo $i| cut -d "=" -f 4)"
		fi
		nomeApp="$(echo $nomeApp | sed 's/\///g')"

		saida=$saida"{ \"{#APPNOME}\":\"$nomeApp\" , \"{#APPCAMINHO}\":\"$i\" },\n"
	done
	saida="$(echo $saida | rev | cut -c 4- | rev)"
	saida=$saida"\\n]}"
	echo -e $saida

   elif [ $tratamento = "4" ]; then
	saida="{\"data\":[\\n"
	for i in $(echo -e $retorno); do
		nomeApp="$(echo $i| cut -d "=" -f 4 | cut -d "," -f 1)"
		if test $(echo $nomeApp | grep "//localhost") ; then
			nomeApp="$(echo $nomeApp | sed 's/\/\/localhost//')"
		fi
		nomeApp="$(echo $nomeApp | sed 's/\///g')"
		if [ -z $nomeApp ]; then 
			nomeApp="localhost" 
		fi
		saida=$saida"{ \"{#J2APPNOME}\":\"$nomeApp\" , \"{#J2APPCAMINHO}\":\"$i\" },\n"
	done
        saida="$(echo $saida | rev | cut -c 4- | rev)"
        saida=$saida"\\n]}"
	echo -e $saida

   elif [ $tratamento = "5" ]; then
	localArqTemp=$(echo "$destListaDeploys/discoverdeploys_$listaInstanciaDeploys" | sed 's/\/\//\//')
	rm -f "${localArqTemp}"
	arqDeployed="$(echo -e $retorno | egrep -o -B 2 "watch\:.+" | cut -d ":" -f 3 | sed 's/\-\-//'| xargs --no-run-if-empty -I {} echo {}\\n)"
	saida="{\"data\":[\\n"
	for i in $(echo -e $arqDeployed); do
		arqNome="$(basename $i)"
		saida=$saida"{ \"{#DEPLOYEDPATH}\":\"$i\" , \"{#DEPLOYEDNAME}\":\"$arqNome\" },\n"
		echo $i >> "${localArqTemp}"
	done
	saida="$(echo $saida | rev | cut -c 4- | rev)"
	saida=$saida"\\n]}"
	echo -e $saida
 
 
   elif [ $tratamento = "6" ]; then
	arqDeployed="$(echo -e $retorno | egrep -o -B 2 "watch\:.+" | cut -d ":" -f 3 | sed 's/\-\-//'| xargs --no-run-if-empty -I {} echo {}\\n)"
	numDeploys=$(cat "$destListaDeploys/discoverdeploys_$listaInstanciaDeploys" 2> /dev/null | wc -l)
	for i in $(cat "$destListaDeploys/discoverdeploys_$listaInstanciaDeploys" 2> /dev/null); do
		if [ -z "$i" ]; then
			continue
		fi
		deployEstado=$(echo -e $retorno | grep -B 2 "watch: file:$i" | xargs --no-run-if-empty -I {} echo {}\\n)
		deployEstado="$(echo $deployEstado | rev | cut -c 3- | rev)"
		
		deployStatus=$(echo -e $deployEstado | awk 'NR==1' | cut -d ":" -f 2)
		deployState=$(echo -e $deployEstado | awk 'NR==2' | cut -d ":" -f 2)

		if [ -z "$deployStatus" ] || [ -z "$deployState" ] || [ -z "$deployEstado" ] ; then
			deployStatus="ERRO"
			deployState="ERRO"
		fi
		
		$pathZabbixSender -s $hostZabbixName -k "Deploy_Status[$i, $listaInstanciaDeploys]" -z 127.0.0.1 -o $deployStatus 2>&1 > /dev/null
		$pathZabbixSender -s $hostZabbixName -k "Deploy_State[$i, $listaInstanciaDeploys]" -z 127.0.0.1 -o $deployState 2>&1 > /dev/null
	done
	echo $numDeploys
   else
	echo -e $retorno
fi


#sudo /opt/jboss-5.1.0.GA/bin/twiddle.sh -s jnp://server:1499 -u usuario -p "pass" get "java.lang:type=OperatingSystem" FreePhysicalMemorySize
#Exemplos
#./callTwiddle.sh server 1499 usario pass DISCOVERDS query "jboss.jca:service=DataSourceBinding,name=*"
#./callTwiddle.sh server 1499 usario pass DS caDS get "jboss.jca:name=DSNOMEDS,service=ManagedConnectionPool" InUseConnectionCount
#./callTwiddle.sh server 1499 usario pass 1 get java.lang:type=OperatingSystem FreePhysicalMemorySize
#./callTwiddle.sh server 1499 usario pass DISCOVERWAPP query "jboss.web:type=Manager,*"
#./callTwiddle.sh server 1499 usario pass DISCOVERAPPJ2EE query "jboss.web:j2eeType=Servlet,name=default,*"
#/opt/jboss-5.1.0.GA/bin/twiddle.sh -s jnp://ingrid:1499 -u admin -p admin_homologa_imprensa query "jboss.web:j2eeType=Servlet,name=default,*"
#
