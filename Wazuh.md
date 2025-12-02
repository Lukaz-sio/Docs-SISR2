# INSTALLATION DE WAZUH 

Installation du serveur web SRV-WEB
Dans un premier temps, nous allons installer une VM SRV-WEB hébergeant une application web de test, DVWA qui
signifie "Damn Vulnerable Web Application". DVWA est intentionnellement vulnérable, utilisée dans le domaine de
la cybersécurité pour s'entraîner aux tests d'intrusion et pour apprendre à sécuriser les applications web. Développée
en PHP avec une base de données MySQL, elle permet aux professionnels de la sécurité, aux étudiants et aux
développeurs de simuler des attaques courantes telles que les injections SQL, le Cross-Site Scripting (XSS) et bien
d'autres.
· Importez une VM Debian. Renommez la et configurez ces paramètres IP.
· Vérifiez que votre serveur web est synchronisé sur le bon fuseau horaire.
timedatectl
timedatectl set-timezone Europe/Paris # si besoin
· Synchronisez votre serveur web sur un serveur NTP, dans le fichier /etc/systemd/timesyncd.conf.
[Time]
NTP=ntp.univ-rennes2.fr
· Activez NTP, redémarrez le service et vérifiez la synchronisation.
timedatectl set-ntp true
systemctl restart systemd-timesyncd.service
timedatectl timesync-status

B3-Act7-TP1 Mise en œuvre d’un SIEM - WAZUH page 4/12
· Utilisez le script ci-dessous pour l’installation de DVWA. Laissez tous les paramètres par défaut. Appuyez sur
ENTREE sans entrez de mot de passe.

```bash
apt install curl

bash -c "$(curl --fail --show-error --silent --location https://raw.githubusercontent.com/IamCarron/DVWA-
Script/main/Install-DVWA.sh)"
```

Le script installe les paquets nécessaires à l’hébergement du site (apache2, mariadb-server, php) et l’application web
DVWA. Ne rentrez pas de mot de passe pendant l’installation, appuyez simplement sur Entrée.
· Vérifiez à partir d’un client, par exemple la Kali, que vous accédez à la page DVWA à l’adresse
http://192.168.0.1/DVWA

Username : admin
Password :password


# Installation de WAZUH

· Importez une VM Ubuntu 22.04 server. Attribuez 4Go de RAM à cette machine. Renommez cette VM SRV-
WAZUH.

· Ubuntu utilise netplan pour la configuration IP des interfaces. Créez un fichier /etc/netplan/99_config.yaml et
suivez l’exemple ci-dessous pour la configuration. Attention à respecter les indentations :

**SANS VLAN**

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
```

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

Utilisez la partie Wazuh agent de la documentation pour installation de l’agent Wazuh sur la VM SRV-WIN1 :
https://documentation.wazuh.com/current/installation-guide/wazuh-agent/index.html. 

Installez le fichier wazuh-agent.msi

https://packages.wazuh.com/4.x/windows/wazuh-agent-4.14.1-1.msi

Ouvrez Powershell en administrateur, allez dans le dossier où le fichier wazuh-agent s'est installé et executez cette commande en remplacant l'IP par celle de votre WAZUH

```powershell
.\wazuh-agent-4.14.1-1.msi /q WAZUH_MANAGER="172.16.0.7"
```

démarrez l'agent wazuh :

```powershell
Start-Service wazuhsvc
```

Ensuite Installez l'agent sur le serveur web 

https://documentation.wazuh.com/current/installation-guide/wazuh-agent/wazuh-agent-package-linux.html

```bash
apt-get install gnupg apt-transport-https
curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | gpg --no-default-keyring --keyring gnupg-ring:/usr/share/keyrings/wazuh.gpg --import && chmod 644 /usr/share/keyrings/wazuh.gpg
echo "deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main" | tee -a /etc/apt/sources.list.d/wazuh.list
apt-get update
```

Déployez l'agent wazuh : 

```bash
WAZUH_MANAGER="172.16.0.7" apt-get install wazuh-agent
```

Redémarrer les services :

```bash
systemctl daemon-reload
systemctl enable wazuh-agent
systemctl start wazuh-agent
```

Vérifiez que l’hôte apparaît sur le dashboard de Wazuh.