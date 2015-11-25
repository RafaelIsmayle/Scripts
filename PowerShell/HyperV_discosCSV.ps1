# Última edição em 16/07/2014 por Dyego M. Bezerra
# Script para verificação de discos Cluster Shared Volume

Param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string] $cluster,
    [string] $disco,
    $pLivre = $true
    ) 

if (!(Get-Module -Name FailoverClusters))
{
    Import-Module -Name FailoverClusters -ErrorAction Stop
}

if (($disco) -and ($pLivre))
{
    "{0:N2}" -f(Get-ClusterSharedVolume -Cluster $cluster $disco | select -Expand SharedVolumeInfo | select -ExpandProperty Partition | select PercentFree).PercentFree
    exit
}

$listaDiscos=Get-ClusterSharedVolume -Cluster $cluster | select Name | ForEach-Object {$_.Name}

foreach ($i in $listaDiscos )
    {
    Write-Host $i
    #"{0:N2}" -f(Get-ClusterSharedVolume -Cluster $cluster $i | select -Expand SharedVolumeInfo | select -ExpandProperty Partition | select PercentFree).PercentFree
    }
