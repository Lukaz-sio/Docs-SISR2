
# Réplication DHCP sur Windows Server

Ce guide explique comment configurer la réplication et le basculement DHCP entre deux serveurs Windows Server.

---

## Prérequis

- Deux serveurs Windows Server avec le rôle DHCP installé.
- Les deux serveurs doivent être sur le même réseau et pouvoir communiquer.

---

## Étapes de configuration

### 1. Installation du rôle DHCP

Installer le rôle DHCP sur les deux serveurs via le Gestionnaire de serveur ou avec PowerShell :

```powershell
Install-WindowsFeature -Name DHCP -IncludeManagementTools
```

### 2. Configuration de l’étendue sur le premier serveur

- Sur le premier serveur, ouvrir la console DHCP.
- Créer et configurer l’étendue (plage d’adresses, options, etc.) ou en Powershell.

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

### 3. Mise en place du basculement DHCP

- Dans la console DHCP du premier serveur :
	- Clic droit sur `IPv4` > `Configurer le basculement...`
	- Sélectionner l’étendue à répliquer.
	- Ajouter le second serveur comme partenaire.

#### Modes de basculement disponibles

**A. Mode Serveur de secours (Hot Standby)**

- Le serveur partenaire prend le relais en cas de panne du serveur principal.
- Paramètres recommandés :
	- Pourcentage de veille : **25%**
	- Intervalle de basculement d’état : **2 minutes**
	- Secret partagé : (exemple) `Btssio2017`

**B. Répartition de charge (Load Balancing)**

- Les deux serveurs distribuent les baux DHCP en parallèle.
- Répartition typique : **50% / 50%**

---

## Bonnes pratiques

- Vérifier la synchronisation des étendues après configuration.
- Tester le basculement en simulant une panne du serveur principal.
- Documenter le secret partagé et le conserver en lieu sûr.

---

## Ressources

- [Documentation Microsoft DHCP Failover](https://learn.microsoft.com/fr-fr/windows-server/networking/technologies/dhcp/dhcp-failover)

---

Ce document est prêt à être utilisé sur GitHub pour la configuration de la réplication DHCP sur Windows Server.