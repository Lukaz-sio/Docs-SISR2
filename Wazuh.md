# 🛡️ Installation de DVWA et Préparation pour Wazuh

Ce document détaille l'installation de la machine hôte **SRV-WEB** (sous Debian) et le déploiement de l'application web vulnérable **DVWA** (Damn Vulnerable Web Application), ainsi que la configuration horaire nécessaire avant l'installation de l'agent Wazuh.

---

## 1. ⚙️ Installation du Serveur Web (SRV-WEB)

### 1.1. Configuration de Base de la VM

1.  Importez une VM Debian, renommez-la et configurez son adresse IP.
2.  Vérifiez et appliquez le fuseau horaire **Europe/Paris** si nécessaire :

    ```bash
    timedatectl
    timedatectl set-timezone Europe/Paris
    ```

### 1.2. Configuration et Synchronisation NTP

La synchronisation horaire est essentielle pour la corrélation des logs par Wazuh.

1.  Éditez le fichier de configuration du service de temps :

    ```bash
    nano /etc/systemd/timesyncd.conf
    ```

2.  Ajoutez ou modifiez la section `[Time]` pour utiliser le serveur NTP de l'université de Rennes2 :

    ```ini
    [Time]
    NTP=ntp.univ-rennes2.fr
    ```

3.  Activez le service NTP, redémarrez-le et vérifiez la synchronisation :

    ```bash
    timedatectl set-ntp true
    systemctl restart systemd-timesyncd.service
    timedatectl timesync-status
    ```

---

## 2. 🌐 Installation de DVWA (Damn Vulnerable Web Application)

DVWA est une application PHP/MySQL vulnérable utilisée pour les tests d'intrusion. Le script ci-dessous installera les dépendances nécessaires (`apache2`, `mariadb-server`, `php`).

1.  Installez `curl` :

    ```bash
    apt install curl
    ```

2.  Exécutez le script d'installation de DVWA. **Appuyez sur ENTRÉE sans entrer de mot de passe** lorsque demandé pour la configuration de MariaDB.

    ```bash
    bash -c "$(curl --fail --show-error --silent --location [https://raw.githubusercontent.com/IamCarron/DVWA-Script/main/Install-DVWA.sh](https://raw.githubusercontent.com/IamCarron/DVWA-Script/main/Install-DVWA.sh))"
    ```

### 2.1. Vérification de l'Accès

1.  Vérifiez l'accès à la page DVWA à partir d’un client (ex: Kali Linux) via l'URL (adaptez l'IP) : **`http://192.168.0.1/DVWA`**.

| Rôle | Valeur |
| :--- | :--- |
| **Username** | `admin` |
| **Password** | `password` |

# 🛡️ Installation de WAZUH (SRV-WAZUH)

Cette section couvre la préparation du serveur **SRV-WAZUH** (sous Ubuntu 22.04) en définissant ses paramètres matériels, sa configuration réseau (avec ou sans VLAN via Netplan), et sa synchronisation horaire NTP.

---

## 1. 🖥️ Préparation de la Machine Virtuelle

1.  Importez une VM **Ubuntu 22.04 Server**.
2.  Attribuez **4 Go de RAM** à cette machine.
3.  Renommez cette VM **`SRV-WAZUH`**.

---

## 2. 🌐 Configuration Réseau avec Netplan

Ubuntu utilise **Netplan** pour gérer la configuration IP. Vous devez créer le fichier `/etc/netplan/99_config.yaml` et respecter scrupuleusement l'indentation YAML.

### 2.1. Configuration Statique Standard (SANS VLAN)

Utilisez cet exemple pour une configuration statique simple sur l'interface **`ens33`** (adaptez le nom de l'interface si nécessaire) :

```yml
network:
  version: 2
  renderer: networkd
  ethernets:
    ens33:
      addresses:
        - 172.16.0.7/24
      routes:
        - to: default
          via: 172.16.0.254
      nameservers:
        search: [sodecaf.local]
        addresses: [172.16.0.1, 8.8.8.8]

**AVEC VLAN**

```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    # 1. Configurer l'interface physique (ne doit pas avoir d'adresse IP)
    eth0:
      dhcp4: no
      dhcp6: no
  
  vlans:
    # 2. Créer la sous-interface VLAN (nom standard: <interface>.<vlan_id>)
    eth0.10:
      # L'interface physique sur laquelle ce VLAN est taggé
      link: eth0
      # L'ID du VLAN
      id: 10
      # Adresses IP souhaitées pour ce VLAN
      addresses: [192.168.10.50/24]
      routes:
        # Définir la passerelle par défaut (gateway) pour ce VLAN
        - to: default
          via: 192.168.10.1
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
```

· Appliquez cette configuration à l’aide de la commande netplan apply.
· Synchronisez votre serveur WAZUH sur le même serveur NTP que le serveur web.
```bash
timedatectl
timedatectl set-timezone Europe/Paris
```

· Synchronisez votre serveur web sur un serveur NTP, dans le fichier `/etc/systemd/timesyncd.conf`.

```bash
[Time]
NTP=ntp.univ-rennes2.fr
```

· Activez NTP, redémarrez le service et vérifiez la synchronisation.

```bash
timedatectl set-ntp true
systemctl restart systemd-timesyncd.service
timedatectl timesync-status
```

**EFFECTUEZ UNE SNAPSHOT DE VOTRE WAZUH**

Un problème de partition peut survenir, pour être sûr, tapez en console cette commande :

```bash
lvextend -r -l +100%FREE /dev/mapper/ubuntu--vg-ubuntu--lv
```

· Téléchargez et exécutez le script d’installation de Wazuh avec la commande :

```bash
curl -sO https://packages.wazuh.com/4.12/wazuh-install.sh && sudo bash ./wazuh-install.sh -a
```

Accédez à l’interface web de Wazuh à l’adresse https://@IP_wazuh/. 
Le compte administrateur a pour login admin et le mot de passe est celui affiché en console à la fin de l’installation.

Si vous perdez le mot de passe admin, vous pouvez, en console, afficher les mots de passe des utilisateurs à l’aide de la commande :

```bash
sudo tar -O -xvf wazuh-install-files.tar wazuh-install-files/wazuh-passwords.txt
```

Vous pouvez aussi modifier le mot de passe admin :

```bash
cd /usr/share/wazuh-indexer/plugins/opensearch-security/tools
bash wazuh-passwords-tool.sh -u admin -p password
```

créez une nouvelle règle dans Stormshield :

| Status | Action | Source | Destination | Dest. Port |
| :---: | :---: | :---: | :---: | :---: |
| ON | PASS | ANY | SRV-WAZUH | 1514, 1515 |

Maintenant que votre installation de Wazuh est prête, vous pouvez commencer à déployer l’agent Wazuh.

Dans Wazuh, allez dans `Deploy New Agent`, selectionner votre OS et mettez l'adresse IP de votre Wazuh dans Server address. Pas besoin de mettre un agent name.

Copier la commande donnée dans la partie 4 et 5.

Pour Debian : 

```bash
wget https://packages.wazuh.com/4.x/apt/pool/main/w/wazuh-agent/wazuh-agent_4.12.0-1_amd64.deb && sudo WAZUH_MANAGER='172.16.0.7' dpkg -i ./wazuh-agent_4.12.0-1_amd64.deb
```

Redémarrez les services :

```bash
sudo systemctl daemon-reload
sudo systemctl enable wazuh-agent
sudo systemctl start wazuh-agent
```

Pour Windows, lancez powershell en administrateur :

```powershell
Invoke-WebRequest -Uri https://packages.wazuh.com/4.x/windows/wazuh-agent-4.12.0-1.msi -OutFile $env:tmp\wazuh-agent; msiexec.exe /i $env:tmp\wazuh-agent /q WAZUH_MANAGER='172.16.0.7' 
```

Démarrer le service :

```powershell
NET START WazuhSvc
```

Vérifiez que les hôtes apparaîssent sur le dashboard de Wazuh.

# Test d’attaque brute force sur SSH

Sur le serveur Wazuh, ouvrez le fichier `/var/ossec/etc/ossec.conf` et vérifiez la présence des lignes ci-dessous :

```xml
<command>
<name>firewall-drop</name>
<executable>firewall-drop</executable>
<timeout_allowed>yes</timeout_allowed>
</command>
```

Dans ce même fichier, il est possible d’ajouter des réponses actives, qui configurent des réponses automatiques à des
événements relevés par Wazuh.

Attention : la commande firewall-drop utilise iptables. Le paquet iptables doit donc être installé sur la machine agent (ici le serveur web).

```bash
apt install iptables
```

Ajoutez alors le bloc ci-dessous au fichier /var/ossec/etc/ossec.conf :

```xml
<active-response>
<command>firewall-drop</command>
<location>local</location>
<rules_id>5763</rules_id>
<timeout>180</timeout>
</active-response>
```

Enregistrez le fichier modifié. Redémarrez le service wazuh-manager.

Effectuez un test de connectivité de la Kali vers le serveur web.

Sur la Kali Linux, lancez l’attaque par force brute du service SSH :

```bash
hydra -t 4 -l etudiant -P /usr/share/wordlists/rockyou.txt.gz 192.168.0.1 ssh
```

Sur l'interface web de Wazuh, allez dans Threat Hunting puis Events et vérifiez qu'il y a bien un évènement d'attaque `sshd: bruteforce trying to get access to the system` et que l'hôte a bien été bloqué par firewall-drop.

Sur le dashboard de Wazuh, allez que l’agent du SRV-WEB, puis Threat Hunting et appliquez le filtre rule.id is 5763. L’attaque par brute force a été détectée.

Ici une attaque avec l’identifiant MITRE T1110 a été détecté, il s’agit du code attribué par le MITRE pour les attaques de type brute force : https://attack.mitre.org/techniques/T1110/
– rule_id 5763 est la règle de détection brute force SSH dans Wazuh
– Elle correspond à la technique MITRE T1110 – Brute Force.
– L’active response applique automatiquement un blocage temporaire de l’IP attaquante.