#!/bin/bash
echo "Script de Teste"
echo "Criando Arquivo de teste na Pasta TMP"
touch arquivodeteste.txt /tmp/
echo "Esrevendo algo no arquivo"
echo "algo escrito no dia $(date) " > /tmp/arquivodeteste.txt
echo "Fim do Script"
