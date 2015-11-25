#! /bin/bash
#
# Ultima modificacao em 08/08/2013 por Dyego Miranda Bezerra
#
 
##########
# Coleta #
##########
 
pathZabbixSender="/usr/bin/zabbix_sender"
varServNome=$1
varServIP=$2

if [ "$3" = "versao" ]; then
        ServStatus2=$(wget --quiet -O - http://$varServIP/server-status)
        ApacheVersion="$(echo "$ServStatus2" | egrep -o 'Server Version: [a-Z|/|0-9|\.|\(|\)|\/| |_|-]+' | awk -F': ' '{print $2}')"
        echo $ApacheVersion
        exit
fi

VAR=$(wget --quiet -O - http://$varServIP/server-status?auto)

#ServStatus2=$(wget --quiet -O - http://$varServIP/server-status)
 
if [[ -z $VAR ]]; then
    echo "ZBX_NOTSUPPORTED"
    exit 1
fi
 
#ApacheVersion="$(echo "$ServStatus2" | egrep -o 'Server Version: [a-Z|/|0-9|\.|\(|\)|\/| |_|-]+' | awk -F': ' '{print $2}')"
#$pathZabbixSender -s $varServNome -k ApacheVersion -z 127.0.0.1 -o "$ApacheVersion" 2>&1 > /dev/null

TotalAccesses="$(echo "$VAR"|grep "Total Accesses:"|awk '{print $3}')"
$pathZabbixSender -s $varServNome -k TotalAccesses -z 127.0.0.1 -o $TotalAccesses 2>&1 > /dev/null
#echo TotalAccesses: $TotalAccesses

TotalKBytes="$(echo "$VAR"|grep "Total kBytes:"|awk '{print $3}')"
$pathZabbixSender -s $varServNome -k TotalKBytes -z 127.0.0.1 -o $TotalKBytes 2>&1 > /dev/null
#echo TotalKBytes: $TotalKBytes

Uptime="$(echo "$VAR"|grep "Uptime:"|awk '{print $2}')"
$pathZabbixSender -s $varServNome -k Uptime -z 127.0.0.1 -o $Uptime 2>&1 > /dev/null
#echo Uptime: $Uptime

ReqPerSec="$(echo "$VAR"|grep "ReqPerSec:"|awk '{print $2}')"
$pathZabbixSender -s $varServNome -k ReqPerSec -z 127.0.0.1 -o $ReqPerSec 2>&1 > /dev/null
#echo ReqPerSec: $ReqPerSec

BytesPerSec="$(echo "$VAR"|grep "BytesPerSec:"|awk '{print $2}')"
$pathZabbixSender -s $varServNome -k BytesPerSec -z 127.0.0.1 -o $BytesPerSec 2>&1 > /dev/null
#echo BytesPerSec: $BytesPerSec

BytesPerReq="$(echo "$VAR"|grep "BytesPerReq:"|awk '{print $2}')"
$pathZabbixSender -s $varServNome -k BytesPerReq -z 127.0.0.1 -o $BytesPerReq 2>&1 > /dev/null
#echo BytesPerReq: $BytesPerReq

BusyWorkers="$(echo "$VAR"|grep "BusyWorkers:"|awk '{print $2}')"
#$pathZabbixSender -s $varServNome -k BusyWorkers -z 127.0.0.1 -o $BusyWorkers 2>&1 > /dev/null
#echo BusyWorkers: $BusyWorkers

IdleWorkers="$(echo "$VAR"|grep "IdleWorkers:"|awk '{print $2}')"
$pathZabbixSender -s $varServNome -k IdleWorkers -z 127.0.0.1 -o $IdleWorkers 2>&1 > /dev/null
#echo IdleWorkers: $IdleWorkers

WaitingForConnection="$(echo "$VAR"|grep "Scoreboard:"| awk '{print $2}'| awk 'BEGIN { FS = "_" } ; { print NF-1 }')"
$pathZabbixSender -s $varServNome -k WaitingForConnection -z 127.0.0.1 -o $WaitingForConnection 2>&1 > /dev/null
#echo WaitingForConnection: $WaitingForConnection

StartingUp="$(echo "$VAR"|grep "Scoreboard:"| awk '{print $2}'| awk 'BEGIN { FS = "S" } ; { print NF-1 }')"
$pathZabbixSender -s $varServNome -k StartingUp -z 127.0.0.1 -o $StartingUp 2>&1 > /dev/null
#echo StartingUp: $StartingUp

ReadingRequest="$(echo "$VAR"|grep "Scoreboard:"| awk '{print $2}'| awk 'BEGIN { FS = "R" } ; { print NF-1 }')"
$pathZabbixSender -s $varServNome -k ReadingRequest -z 127.0.0.1 -o $ReadingRequest 2>&1 > /dev/null
#echo ReadingRequest: $ReadingRequest

SendingReply="$(echo "$VAR"|grep "Scoreboard:"| awk '{print $2}'| awk 'BEGIN { FS = "W" } ; { print NF-1 }')"
$pathZabbixSender -s $SendingReply -k BusyWorkers -z 127.0.0.1 -o $SendingReply 2>&1 > /dev/null
#echo SendingReply: $SendingReply

KeepAlive="$(echo "$VAR"|grep "Scoreboard:"| awk '{print $2}'| awk 'BEGIN { FS = "K" } ; { print NF-1 }')"
$pathZabbixSender -s $varServNome -k KeepAlive -z 127.0.0.1 -o $KeepAlive 2>&1 > /dev/null
#echo KeepAlive: $KeepAlive

DNSLookup="$(echo "$VAR"|grep "Scoreboard:"| awk '{print $2}'| awk 'BEGIN { FS = "D" } ; { print NF-1 }')"
$pathZabbixSender -s $varServNome -k DNSLookup -z 127.0.0.1 -o $DNSLookup 2>&1 > /dev/null
#echo DNSLookup: $DNSLookup

ClosingConnection="$(echo "$VAR"|grep "Scoreboard:"| awk '{print $2}'| awk 'BEGIN { FS = "C" } ; { print NF-1 }')"
$pathZabbixSender -s $varServNome -k ClosingConnection -z 127.0.0.1 -o $ClosingConnection 2>&1 > /dev/null
#echo ClosingConnection: $ClosingConnection

Logging="$(echo "$VAR"|grep "Scoreboard:"| awk '{print $2}'| awk 'BEGIN { FS = "L" } ; { print NF-1 }')"
$pathZabbixSender -s $varServNome -k Logging -z 127.0.0.1 -o $Logging 2>&1 > /dev/null
#echo Logging: $Logging

GracefullyFinishing="$(echo "$VAR"|grep "Scoreboard:"| awk '{print $2}'| awk 'BEGIN { FS = "G" } ; { print NF-1 }')"
$pathZabbixSender -s $varServNome -k GracefullyFinishing -z 127.0.0.1 -o $GracefullyFinishing 2>&1 > /dev/null
#echo GracefullyFinishing: $GracefullyFinishing

IdleCleanupOfWorker="$(echo "$VAR"|grep "Scoreboard:"| awk '{print $2}'| awk 'BEGIN { FS = "I" } ; { print NF-1 }')"
$pathZabbixSender -s $varServNome -k IdleCleanupOfWorker -z 127.0.0.1 -o $IdleCleanupOfWorker 2>&1 > /dev/null
#echo IdleCleanupOfWorker: $IdleCleanupOfWorker

OpenSlotWithNoCurrentProcess="$(echo "$VAR"|grep "Scoreboard:"| awk '{print $2}'| awk 'BEGIN { FS = "." } ; { print NF-1 }')"
$pathZabbixSender -s $varServNome -k OpenSlotWithNoCurrentProcess -z 127.0.0.1 -o $OpenSlotWithNoCurrentProcess 2>&1 > /dev/null
#echo OpenSlotWithNoCurrentProcess: $OpenSlotWithNoCurrentProcess

echo $BusyWorkers
