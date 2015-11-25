@ECHO OFF
cls
echo.
echo.
set zabbixServer=192.168.0.111,192.168.20.111
set zabbixServerActive=192.168.0.111
set localZabbix=%ProgramFiles%\Zabbix
set arquivosInstal=\\jacqueline\compartilhamento\zabbix\bin

echo Servidor zabbix: %zabbixServer%
echo Local de instalacao do agente: %localZabbix%

mkdir "%localZabbix%"
echo.
echo.
echo Nome agente: %COMPUTERNAME%


if /i "%PROCESSOR_ARCHITECTURE%" equ "AMD64" (
echo Arquitetura do processador: 64 bits
pause
copy "%arquivosInstal%\win64\*" "%localZabbix%"

) else if /i "%PROCESSOR_ARCHITECTURE%" equ "x86" (
echo Arquitetura do processador: 32 bits
pause
copy "%arquivosInstal%\win32\*" "%localZabbix%"
) else (
echo [ERRO] Arquitetura do computador nao encontrada!
exit
)

echo #Configuração gerada via script > "%localZabbix%\zabbix_agentd.conf"
echo LogFile=%localZabbix%\zabbix_agentd.log >> "%localZabbix%\zabbix_agentd.conf"
echo LogFileSize=0 >> "%localZabbix%\zabbix_agentd.conf"
echo Server=%zabbixServer% >> "%localZabbix%\zabbix_agentd.conf"
echo ServerActive=%zabbixServerActive% >> "%localZabbix%\zabbix_agentd.conf"
echo Hostname=%COMPUTERNAME% >> "%localZabbix%\zabbix_agentd.conf"

cd "%localZabbix%"
echo INSTALANDO SERVICO DO AGENTE ZABBIX:
zabbix_agentd.exe -i -c zabbix_agentd.conf

net start "Zabbix Agent"

pause
