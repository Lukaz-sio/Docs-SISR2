# Documentation Zabbix

## Table des matières
- [Prérequis](#prérequis)
- [Installation du serveur Zabbix](#installation-du-serveur-zabbix)
  - [Configuration système](#configuration-système)
  - [Installation des dépendances](#installation-des-dépendances)
  - [Configuration de la base de données](#configuration-de-la-base-de-données)
  - [Configuration de Zabbix](#configuration-de-zabbix)
- [Configuration de l'agent Windows](#configuration-de-lagent-windows)
- [Configuration SNMP](#configuration-snmp)

## Prérequis

- Machine virtuelle Debian 12
- Connexion Internet fonctionnelle
- Accès root ou sudo

## Installation du serveur Zabbix

### Configuration système

1. Renommer le système :
   ```bash
   # Modifier /etc/hosts et /etc/hostname
   # Remplacer "debian" par "zabbix"
   nano /etc/hosts
   nano /etc/hostname
   ```

2. Mettre à jour le système :
   ```bash
   apt update
   apt upgrade -y
   ```

### Installation des dépendances

1. Installer les services web et base de données :
   ```bash
   apt install apache2 mariadb-server
   ```

2. Télécharger Zabbix :
   - Visiter [le site de Zabbix](https://www.zabbix.com/fr/download)
   - Sélectionner :
     - Version : dernière version (7.4)
     - OS : Debian 12
     - Composants : Server, Frontend, Agent
     - Base de données : MySQL
     - Serveur Web : Apache

### Installation de Zabbix

1. Ajouter le dépôt Zabbix :
   ```bash
   wget https://repo.zabbix.com/zabbix/7.4/release/debian/pool/main/z/zabbix-release/zabbix-release_latest_7.4+debian12_all.deb
   dpkg -i zabbix-release_latest_7.4+debian12_all.deb
   apt update
   ```

2. Installer les composants Zabbix :
   ```bash
   apt install zabbix-server-mysql zabbix-frontend-php zabbix-apache-conf zabbix-sql-scripts zabbix-agent
   ```

### Configuration de la base de données

1. Créer la base de données et l'utilisateur :
   ```bash
   mysql -uroot -p
   ```
   
   Exécuter les commandes SQL suivantes :
   ```sql
   create database zabbix character set utf8mb4 collate utf8mb4_bin;
   create user zabbix@localhost identified by 'password';
   grant all privileges on zabbix.* to zabbix@localhost;
   set global log_bin_trust_function_creators = 1;
   quit;
   ```

   > **Note**: Remplacez 'password' par un mot de passe sécurisé de votre choix
2. Importer le schéma de base de données :
   ```bash
   zcat /usr/share/zabbix/sql-scripts/mysql/server.sql.gz | mysql --default-character-set=utf8mb4 -uzabbix -p zabbix
   ```

3. Désactiver l'option `log_bin_trust_function_creators` :
   ```bash
   mysql -uroot -p
   ```
   ```sql
   set global log_bin_trust_function_creators = 0;
   quit;
   ```

### Configuration de Zabbix

1. Configurer la connexion à la base de données :
   ```bash
   # Éditer le fichier /etc/zabbix/zabbix_server.conf
   nano /etc/zabbix/zabbix_server.conf
   ```
   
   Ajouter/modifier la ligne :
   ```ini
   DBPassword=password
   ```

2. Démarrer et activer les services :
   ```bash
   # Démarrer les services
   systemctl restart zabbix-server zabbix-agent apache2
   
   # Activer le démarrage automatique
   systemctl enable zabbix-server zabbix-agent apache2
   ```

### Configuration de l'interface Web

1. Accéder à l'interface web :
   - Ouvrir un navigateur
   - Accéder à `http://<IP_DU_SERVEUR>/zabbix`

2. Configuration initiale :
   - Utiliser le mot de passe défini dans la configuration MySQL
   - Configurer le nom du serveur : `zabbix`
   - Définir le fuseau horaire : `(UTC+01:00)Europe/Paris`

3. Première connexion :
   - Utilisateur : `Admin`
   - Mot de passe : `zabbix`

## Configuration de l'agent Windows

### Installation de l'agent

1. Sur le serveur Windows (AD, DHCP, DNS) :
   - Visiter [le site de Zabbix](https://www.zabbix.com/download_agents)
   - Sélectionner :
     - Windows
     - Server 2016+
     - amd64
     - Version 7.4
     - OpenSSL
     - Format MSI

2. Installation de l'agent :
   - Exécuter le fichier MSI téléchargé
   - Configurer :
     - IP du serveur Zabbix
     - Nom de l'hôte

### Configuration SNMP

1. Installation du service SNMP :
   - Ouvrir le Gestionnaire de serveur
   - Ajouter la fonctionnalité SNMP

2. Configuration SNMP :
   - Ouvrir Services
   - Localiser le service SNMP
   - Dans Propriétés → Sécurité :
     - Créer une communauté : `Sodecaf`
     - Autoriser uniquement l'hôte Zabbix : `172.16.0.5`

3. Activation des services :
   ```powershell
   # Démarrer SNMP
   Start-Service SNMP
   # Démarrer l'agent Zabbix
   Start-Service "Zabbix Agent"
   ```

### Ajout de l'hôte dans Zabbix

1. Créer un groupe d'hôtes :
   - Aller dans : Configuration → Collecte de données → Groupes d'hôtes
   - Cliquer sur "Créer un groupe d'hôtes"
   - Nom : `Windows-Serveur`

2. Ajouter l'hôte :
   - Aller dans : Configuration → Collecte de données → Hôtes
   - Cliquer sur "Créer un hôte"
   - Nom : `WIN-SRV1`
   - Groupe : `Windows-Serveur`
   - Adresse IP : `<IP_DU_SERVEUR_WINDOWS>` 
