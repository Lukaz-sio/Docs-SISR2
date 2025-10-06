Nous allons maintenant effectuer deux étapes importantes pour la mise en place d’un serveur Windows contrôleur de
domaine :
– Installation de la fonctionnalité AD-Domain-Service (ADDS) ;
– Promotion du serveur en tant que contrôleur de domaine.
Le script est le suivant :

```powershell
$DomainNameDNS = "sodecaf.local"
$DomainNameNetbios = "SODECAF"
$ForestConfiguration = @{
'-DatabasePath'= 'C:\Windows\NTDS';
'-DomainMode' = 'Default';
'-DomainName' = $DomainNameDNS;
'-DomainNetbiosName' = $DomainNameNetbios;
'-ForestMode' = 'Default';
'-InstallDns' = $true;
'-LogPath' = 'C:\Windows\NTDS';
'-NoRebootOnCompletion' = $false;
'-SysvolPath' = 'C:\Windows\SYSVOL';
'-Force' = $true;
'-CreateDnsDelegation' = $false }
Install-WindowsFeature -name AD-Domain-Services -IncludeManagementTools
Install-ADDSForest @ForestConfiguration
Restart-Computer
```

Installation du DHCP en Powershell :

```powershell
$DomainNameDNS = "sodecaf.local"
$IPServeur = "172.16.0.1"

# Installation du rôle DHCP
Install-WindowsFeature -Name DHCP -IncludeManagementTools
# Création du groupe de sécurité
Add-DhcpServerSecurityGroup
# Redémarrage du service DHCP
Restart-Service dhcpserver
# Autorisation du serveur DHCP dans l'annuaire AD
Add-DhcpServerInDC -DnsName $DomainNameDNS -IPAddress $IPServeur
Set-ItemProperty -Path registry::HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\ServerManager\Roles\12 -Name ConfigurationState -Value 2
```

Création d'une étendue DHCP en Powershell :

```powershell
# Script - création d'une étendue DHCP

$NomEtendue = "DHCP_sodecaf"
$IPreseau = "172.16.0.0"
$DebutEtendueDHCP = "172.16.0.150"
$FinEtendueDHCP = "172.16.0.200"
$MasqueIP = "255.255.255.0"
$IPPasserelle = "172.16.0.254"
$IPDNSPrimaire = "172.16.0.1"
$IPDNSSecondaire = "8.8.8.8"
$DomainNameDNS = "sodecaf.local"
$DureeBail = "14400" # durée du bail = 4h
$nomServeurDHCP = "SRV-WIN-CORE1"

# Effacement de l'étendue si existante
if ((Get-DhcpServerv4Scope -ComputerName $nomServeurDHCP) -ne $null) {
	write-host ("Etendue déjà présente, elle sera supprimée")
	Remove-DhcpServerv4Scope -ScopeId $IPreseau -Force
}

# Création de l'étendue
Add-DhcpServerv4Scope -Name $NomEtendue -StartRange $DebutEtendueDHCP  -EndRange $FinEtendueDHCP -SubnetMask $MasqueIP
Set-DhcpServerv4OptionValue -ScopeId $IPreseau -OptionId 3 -Value $IPPasserelle
Set-DhcpServerv4OptionValue -ScopeId $IPreseau -OptionId 6 -Value $IPDNSPrimaire,$IPDNSSecondaire -Force
Set-DhcpServerv4OptionValue -ScopeId $IPreseau -OptionId 15 -Value $DomainNameDNS
Set-DhcpServerv4OptionValue -ScopeId $IPreseau -OptionId 51 -Value $DureeBail

# Activation de l'étendue
Set-DhcpServerv4Scope -ScopeId $IPreseau -Name $NomEtendue -State Active

# Affichage des informations de l'étendue créée
Get-DhcpServerv4Scope -ScopeId $IPreseau
Get-DhcpServerv4OptionValue -ComputerName $nomServeurDHCP -ScopeId $IPreseau

# Supprimer une étendue
# Remove-DhcpServerv4Scope -ScopeId $IPreseau -Force
```

# Installation des fonctionnalités RSAT en powershell sur Win10-Tiny
1. Visualiser les fonctionnalités installées
```powershell
Get-WindowsCapability -Name "RSAT*" -Online | Select-Object -Property DisplayName, State
```
2. Visualiser les noms techniques des fonctionalités RSAT
```powershell
Get-WindowsCapability -Name "RSAT*" -Online | Select-Object -Property Name, DisplayName
```
3. Installer une fonctionnalité
```powershell
Add-WindowsCapability -Online -Name "<nom de l'outil RSAT>"
```

Ajouter la machine Win-Core dans le gestionnaire de serveur :

ouvrir le gestionnaire de serveur sur la machine win 10 tiny puis dans Gérer ajouter des serveurs, dans DNS mettre l'ip de la machine WinCore , cliquer sur la flèche au milieu pour la faire aller sur la fenêtre de droite puis OK et se login avec les identifiants. Puis faire clic droit sur le serveur et gérer en tant que puis encore de login. 


