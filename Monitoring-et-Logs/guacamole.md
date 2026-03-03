# 🥑 Installation et Configuration d'Apache Guacamole sur Debian 12

Ce document détaille l'installation d'Apache Guacamole en tant que bastion d'accès distant (RDP, SSH, VNC) utilisant une base de données MariaDB et une authentification double facteur (TOTP).

---

## 1. ⚙️ Installation des Prérequis Système

### 1.1. Dépendances de compilation et protocoles
Installez les paquets nécessaires pour la compilation et le support des différents protocoles (RDP, SSH, VNC) :

```bash
sudo apt-get update
sudo apt-get install -y build-essential libcairo2-dev libjpeg62-turbo-dev libpng-dev libtool-bin uuid-dev libossp-uuid-dev libavcodec-dev libavformat-dev libavutil-dev libswscale-dev freerdp2-dev libpango1.0-dev libssh2-1-dev libtelnet-dev libvncserver-dev libwebsockets-dev libpulse-dev libssl-dev libvorbis-dev libwebp-dev
```

## 2. 🛠️ Compilation et Installation de Guacamole Server

### 2.1. Téléchargement et compilation
Nous utilisons la version **1.6.0**.

```bash
cd /tmp
wget https://downloads.apache.org/guacamole/1.6.0/source/guacamole-server-1.6.0.tar.gz
tar -xzf guacamole-server-1.6.0.tar.gz
cd guacamole-server-1.6.0/

# Configuration (désactivation de guacenc si erreur FFmpeg)
sudo ./configure --with-systemd-dir=/etc/systemd/system/

# Compilation et installation
sudo make
sudo make install
sudo ldconfig
```

### 2.2. Démarrage du service guacd
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now guacd
```

On vérifie le statut d'Apache Guacamole Server :
```bash
sudo systemctl status guacd
```

### 2.3. Créer le répertoire de configuration
```bash
sudo mkdir -p /etc/guacamole/{extensions,lib}
```

## 3. 🌐 Installation de Guacamole Client (Web App)

Guacamole nécessite **Tomcat 9**. Sur Debian 12, il faut utiliser les dépôts de Debian 11 (Bullseye).

### 3.1. Configuration du dépôt Bullseye
```bash
echo "deb http://deb.debian.org/debian/ bullseye main" | sudo tee /etc/apt/sources.list.d/bullseye.list
sudo apt-get update
sudo apt-get install -y tomcat9 tomcat9-admin tomcat9-common tomcat9-user
```

### 3.2. Déploiement du fichier .war
```bash
cd /tmp
wget https://downloads.apache.org/guacamole/1.6.0/binary/guacamole-1.6.0.war
sudo mv guacamole-1.6.0.war /var/lib/tomcat9/webapps/guacamole.war
sudo systemctl restart tomcat9
```

## 4. 🗄️ Configuration de la Base de Données MariaDB

### 4.1. Création de la base et de l'utilisateur
```bash
sudo apt-get install -y mariadb-server
sudo mysql_secure_installation

sudo mysql -u root -p
```

```sql
CREATE DATABASE guacadb;
CREATE USER 'guaca_nachos'@'localhost' IDENTIFIED BY 'P@ssword!';
GRANT SELECT,INSERT,UPDATE,DELETE ON guacadb.* TO 'guaca_nachos'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 4.2. Installation des extensions JDBC et Connecteur MySQL
```bash
sudo mkdir -p /etc/guacamole/{extensions,lib}

# Extension JDBC
cd /tmp
wget https://downloads.apache.org/guacamole/1.5.5/binary/guacamole-auth-jdbc-1.6.0.tar.gz
tar -xzf guacamole-auth-jdbc-1.6.0.tar.gz
sudo mv guacamole-auth-jdbc-1.6.0/mysql/guacamole-auth-jdbc-mysql-1.6.0.jar /etc/guacamole/extensions/

# Connecteur MySQL J
wget https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-j-9.6.0.tar.gz
tar -xzf mysql-connector-j-9.6.0.tar.gz
sudo cp mysql-connector-j-9.6.0/mysql-connector-j-9.6.0.jar /etc/guacamole/lib/
```

### 4.3. Import du schéma SQL
```bash
cd /tmp/guacamole-auth-jdbc-1.6.0/mysql/schema/
cat *.sql | mysql -u root -p guacadb
```

## 5. 📝 Fichiers de Configuration

### 5.1. /etc/guacamole/guacamole.properties
```ini
# MySQL Connection
mysql-hostname: 127.0.0.1
mysql-port: 3306
mysql-database: guacadb
mysql-username: guaca_nachos
mysql-password: P@ssword!
```

### 5.2. /etc/guacamole/guacd.conf
```ini
[server]
bind_host = 0.0.0.0
bind_port = 4822
```

Redémarrez les services :
```bash
sudo systemctl restart tomcat9 guacd mariadb
```

---

## 6. 🚀 Premiers Pas et Sécurisation

**URL d'accès :** `http://<IP_SERVEUR>:8080/guacamole/`
**Identifiants par défaut :** `guacadmin` / `guacadmin`

### 6.1. Sécurisation du compte Admin
1. Allez dans **Paramètres > Utilisateurs**.
2. Créez un nouvel utilisateur administrateur avec toutes les permissions.
3. Déconnectez-vous, reconnectez-vous avec le nouveau compte.
4. Supprimez ou désactivez le compte `guacadmin`.

### 6.2. Configuration du MFA (TOTP)
```bash
cd /tmp
wget https://downloads.apache.org/guacamole/1.5.5/binary/guacamole-auth-totp-1.5.5.tar.gz
tar -xzf guacamole-auth-totp-1.5.5.tar.gz
sudo mv guacamole-auth-totp-1.5.5/guacamole-auth-totp-1.5.5.jar /etc/guacamole/extensions/
```
Ajoutez au fichier `guacamole.properties` :
```ini
# TOTP
totp-issuer: Guacamole SISR
totp-digits: 6
totp-period: 30
totp-mode: sha1
```
Redémarrez Tomcat : `sudo systemctl restart tomcat9`.

---

## 7. 🎥 Enregistrement des Sessions

### 7.1. Installation de l'extension
```bash
cd /tmp
wget https://downloads.apache.org/guacamole/1.5.5/binary/guacamole-history-recording-storage-1.5.5.tar.gz
tar -xzf guacamole-history-recording-storage-1.5.5.tar.gz
sudo mv guacamole-history-recording-storage-1.5.5/guacamole-history-recording-storage-1.5.5.jar /etc/guacamole/extensions/
```

### 7.2. Configuration du stockage
```bash
sudo mkdir -p /var/lib/guacamole/recordings
sudo chown root:tomcat /var/lib/guacamole/recordings
sudo chmod 2750 /var/lib/guacamole/recordings
sudo systemctl restart tomcat9
```

### 7.3. Paramètres de la connexion (Interface Web)
Dans la section **Enregistrement écran** d'une connexion :
* **Chemin :** `${HISTORY_PATH}/${HISTORY_UUID}`
* **Nom :** `${GUAC_DATE}-${GUAC_TIME} - ${GUAC_USERNAME}`
* **Cochez :** "Créer automatiquement un chemin d'enregistrement".

---

## ⚠️ Dépannage (Troubleshooting)

### Erreur de négociation RDP / Certificat
Si la connexion échoue avec une erreur de certificat :
1. Cochez **"Ignorer le certificat du serveur"** dans les paramètres de la connexion.

### Problème de droits guacd (daemon)
Si `guacd` rencontre des problèmes de permissions, créez un utilisateur dédié :
```bash
sudo useradd -M -d /var/lib/guacd/ -r -s /sbin/nologin -c "Guacd User" guacd
sudo mkdir /var/lib/guacd
sudo chown -R guacd: /var/lib/guacd
sudo sed -i 's/daemon/guacd/' /etc/systemd/system/guacd.service
sudo systemctl daemon-reload
sudo systemctl restart guacd
```

### Variables utiles pour le SSO
Pour éviter de ressaisir les identifiants si Guacamole est lié à un LDAP/AD :
* Identifiant : `${GUAC_USERNAME}`
* Mot de passe : `${GUAC_PASSWORD}`

---
*Source : Documentation IT-Connect - Installation Apache Guacamole sur Debian*