# 🚀 Installation de Graylog 6.1 sur Debian 12

Ce document détaille les étapes de configuration système, d'installation des prérequis (MongoDB, OpenSearch) et de déploiement de Graylog Server 6.1 sur une machine Debian 12.

---

## 1. ⚙️ Configuration Initiale du Système

### 1.1. Configuration Réseau et Nom de la Machine

1.  Configurer l'IP de la machine Debian et modifier son nom :

```bash
nano /etc/network/interfaces
```

### 1.2. Configuration du Fuseau Horaire

1.  Appliquer le fuseau horaire **Europe/Paris** :

```bash
timedatectl set-timezone Europe/Paris
```

### 1.3. Configuration et Synchronisation NTP

Nous synchronisons l’horloge avec le serveur de l’université de Rennes2, avec des serveurs de pool en secours.

1.  Éditez le fichier `/etc/systemd/timesyncd.conf` et paramétrez les serveurs de temps :

```bash
nano /etc/systemd/timesyncd.conf
```

```ini
[Time]
NTP=ntp.univ-rennes2.fr
FallbackNTP=0.debian.pool.ntp.org 1.debian.pool.ntp.org 2.debian.pool.ntp.org 3.debian.pool.ntp.org
```

2.  Définir le service NTP comme actif :

```bash
timedatectl set-ntp true
```

3.  Vérifiez la synchronisation (peut prendre quelques minutes) :

```bash
timedatectl
timedatectl timesync-status
```

### 1.4. Mise à Jour du Système

```bash
apt update 
apt upgrade -y
```

## 2. 💾 Installation des Prérequis : MongoDB (v6.0)

### 2.1. Ajout du Dépôt et de la Clé MongoDB

1.  Installer les paquets nécessaires et ajouter la clé GPG MongoDB :

```bash
apt-get install curl lsb-release ca-certificates gnupg2 pwgen

curl -fsSL [https://www.mongodb.org/static/pgp/server-6.0.asc](https://www.mongodb.org/static/pgp/server-6.0.asc) | gpg -o /usr/share/keyrings/mongodb-server-6.0.gpg --dearmor
```

2.  Ajouter le dépôt MongoDB 6.0 (notez que `bullseye` est utilisé pour Debian 12) :

```bash
echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg] [http://repo.mongodb.org/apt/debian](http://repo.mongodb.org/apt/debian) bullseye/mongodb-org/6.0 main" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list
```

3.  Mise à jour et installation de la dépendance `libssl1.1` (nécessaire pour MongoDB 6.0 sur Debian 12) :

```bash
apt update
wget [http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2.24_amd64.deb](http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2.24_amd64.deb)
dpkg -i libssl1.1_1.1.1f-1ubuntu2.24_amd64.deb
```

4.  Installer MongoDB :

```bash
apt-get install -y mongodb-org
apt update
```

### 2.2. Démarrage et Activation de MongoDB

1.  Recharger le service, l'activer au démarrage et le démarrer :

```bash
systemctl daemon-reload
systemctl enable mongod.service
systemctl restart mongod.service
```

2.  Vérifier que le service est actif :

```bash
systemctl --type=service --state=active | grep mongod
```

## 3. 🔎 Installation des Prérequis : OpenSearch (v2.x)

### 3.1. Ajout du Dépôt OpenSearch

1.  Ajouter la clé de signature pour les paquets OpenSearch :

```bash
curl -o- [https://artifacts.opensearch.org/publickeys/opensearch.pgp](https://artifacts.opensearch.org/publickeys/opensearch.pgp) | gpg --dearmor --batch --yes -o /usr/share/keyrings/opensearch-keyring
```

2.  Ajouter le dépôt OpenSearch 2.x :

```bash
echo "deb [signed-by=/usr/share/keyrings/opensearch-keyring] [https://artifacts.opensearch.org/releases/bundle/opensearch/2.x/apt](https://artifacts.opensearch.org/releases/bundle/opensearch/2.x/apt) stable main" | tee /etc/apt/sources.list.d/opensearch-2.x.list
```

3.  Mettre à jour la liste des paquets :

```bash
apt-get update
```

### 3.2. Installation d'OpenSearch

L'installation nécessite de définir un **mot de passe administrateur initial** robuste (min. 8 caractères, incluant min./maj., chiffre, spécial).

1.  Installer OpenSearch (remplacez `Rootsio2017!` par votre mot de passe) :

```bash
env OPENSEARCH_INITIAL_ADMIN_PASSWORD=Rootsio2017! apt-get install opensearch
```

### 3.3. Configuration Minimale d'OpenSearch

1.  Ouvrir le fichier de configuration YAML :

```bash
nano /etc/opensearch/opensearch.yml
```

2.  Ajoutez ou modifiez les lignes suivantes :

```yaml
cluster.name: graylog
node.name: ${HOSTNAME}
path.data: /var/lib/opensearch
path.logs: /var/log/opensearch
discovery.type: single-node
network.host: 127.0.0.1
action.auto_create_index: false
plugins.security.disabled: true
```

### 3.4. Configuration de la JVM (Mémoire Allouée)

Ajustez la mémoire allouée à OpenSearch (ici **2 Go**) dans le fichier de configuration de la JVM (`/etc/opensearch/jvm.options`).

1.  Éditez le fichier de configuration :

```bash
nano /etc/opensearch/jvm.options
```

2.  Remplacez les lignes suivantes pour allouer 2 Go :

| Ancien | Nouveau |
| :--- | :--- |
| `-Xms1g` | `-Xms2g` |
| `-Xmx1g` | `-Xmx2g` |

### 3.5. Démarrage et Vérification d'OpenSearch

1.  Activer le démarrage automatique et lancer le service :

```bash
systemctl daemon-reload
systemctl enable opensearch
systemctl restart opensearch
```

2.  Vérifiez l'utilisation de la mémoire :

```bash
top
```

## 4. 🚀 Installation et Configuration de Graylog Server (v6.1)

### 4.1. Installation du Paquet Graylog

1.  Exécutez les 4 commandes suivantes pour télécharger et installer Graylog Server 6.1 :

    ```bash
    wget [https://packages.graylog2.org/repo/packages/graylog-6.1-repository_latest.deb](https://packages.graylog2.org/repo/packages/graylog-6.1-repository_latest.deb)
    dpkg -i graylog-6.1-repository_latest.deb
    apt-get update
    apt-get install graylog-server
    ```

### 4.2. Configuration de `password_secret` et `root_password_sha2`

Ces deux paramètres sont essentiels pour la sécurité et doivent être configurés dans le fichier `/etc/graylog/server/server.conf`.

1.  Générez une clé aléatoire de 96 caractères pour le paramètre `password_secret` :

    ```bash
    pwgen -N 1 -s 96
    ```

2.  **Copiez la valeur** retournée, puis ouvrez le fichier de configuration :

    ```bash
    nano /etc/graylog/server/server.conf
    ```

3.  Collez la clé au niveau du paramètre `password_secret`.

4.  Générez le hash **SHA-256** de votre mot de passe administrateur (remplacez `Rootsio2017` par votre mot de passe) :

    ```bash
    echo -n "Rootsio2017" | shasum -a 256
    ```

5.  **Copiez la valeur obtenue** (sans le tiret en bout de ligne).

6.  Collez cette valeur dans le fichier de configuration au niveau de l'option `root_password_sha2`.

### 4.3. Configuration d'Accès et Liaison OpenSearch

Modifiez les options suivantes dans le fichier `/etc/graylog/server/server.conf` :

1.  Définir l'adresse d'écoute de l'interface web (accessible sur le port 9000 par toutes les IPs) :

    ```ini
    http_bind_address = 0.0.0.0:9000
    ```

2.  Déclarer l'instance OpenSearch locale :

    ```ini
    elasticsearch_hosts = [http://127.0.0.1:9200](http://127.0.0.1:9200)
    ```

3.  Définir le fuseau horaire de l'interface d'administration :

    ```ini
    root_timezone = Europe/Paris
    ```

4.  Enregistrez et fermez le fichier.

### 4.4. Démarrage de Graylog

1.  Activer le démarrage automatique et lancer immédiatement le serveur Graylog :

    ```bash
    systemctl enable --now graylog-server
    ```

### 4.5. Accès à l'Interface Web

| Rôle | Valeur |
| :--- | :--- |
| **URL d'accès** | `http://172.16.0.6:9000` (Remplacez l'IP par celle de votre machine Debian 12) |
| **Login** | `admin` |
| **Mot de passe** | `Rootsio2017` (ou le mot de passe défini) 

# 💻 Documentation Graylog : Centralisation des Logs

Cette documentation couvre les étapes nécessaires pour centraliser les logs Windows, Linux et Stormshield vers un serveur Graylog.

---

## 1. ⚙️ Importer des Logs de Test (Fichier `logs.txt`)

Avant l’import d’un fichier logs de test, trois étapes sont nécessaires : la création d'un **Input**, d'un **Index**, et d'un **Stream**.

### 1.1. Création de l’Input TCP (Point d'Entrée)

1.  Sous l’interface web de Graylog, allez dans le menu **System > Inputs**.
2.  Choisissez **Raw/Plaintext TCP** puis **Launch new input**.
3.  Entrez le titre **`Graylog_TCP_test_Linux`**. Laissez les autres paramètres par défaut.
4.  Validez. Graylog écoute sur le port **`5555`**.

### 1.2. Création de l’Index (Stockage)

1.  Sur Graylog, cliquez sur **System > Indices > Create index set**.
2.  Choisissez le template **7-days hot**.
3.  Entrez les éléments d'identification pour ces logs (ex: `web-test`).

### 1.3. Création et Liaison du Stream (Routage)

1.  Allez dans **Streams → Create Stream**.
2.  Nommez le Stream (ex: `web-test`) et liez-le à l'Index créé précédemment.
3.  Sur la ligne du Stream créé, cliquez sur **More** puis **Manage rules**.
4.  Ajoutez une règle : Type **"match input"** et sélectionnez l'Input **`Graylog_TCP_test_Linux`**.
5.  Validez avec le bouton **"Create Rule"**.

### 1.4. Import des Logs via Script Batch

Copiez ce script dans un fichier **`script.bat`** et exécutez-le depuis le dossier contenant votre fichier `logs.txt` (nécessite l'outil `ncat` de Nmap).

```batch
@echo off
set GRAYLOG_HOST=172.16.0.6
set GRAYLOG_PORT=5555

for /f "delims=" %%l in (logs.txt) do (
    echo %%l | "C:\Program Files (x86)\Nmap\ncat.exe" %GRAYLOG_HOST% %GRAYLOG_PORT%
)
```

## 2. 🐧 Centralisation des Logs Linux (rsyslog)

### 2.1. Configuration de Graylog

| Composant | Type | Nom | Paramètres Clés |
| :--- | :--- | :--- | :--- |
| **Input** | Syslog UDP | `Graylog_UDP_rsyslog_input` | Port : **12514** ; Time Zone : **`UTC+01:00-Europe/Paris`** ; Cochez : **`store full message ?`** |
| **Index** | N/A | `linux-index` | **System / Indices > Create index set** |
| **Stream** | N/A | `linux-stream` | Index Set : **`linux-index`** ; Cochez : **`Remove matches from 'Default Stream'`** |

**Liaison Stream/Input :** Sur le Stream `linux-stream`, **Manage Rules** > **Add Stream Rule** : Type **`match input`** et sélectionnez **`Graylog_UDP_rsyslog_input`**.

### 2.2. Configuration du Serveur Linux (rsyslog)

1.  Installez `rsyslog` (si ce n'est pas déjà fait) :

    ```bash
    apt install rsyslog
    ```

2.  Créez le fichier de configuration :

    ```bash
    nano /etc/rsyslog.d/1-Linux-graylog
    ```

3.  Insérez la ligne suivante pour envoyer tous les logs (`*.*`) en UDP (`@`) :

    ```ini
    *.* @172.16.0.6:12514;RSYSLOG_SyslogProtocol23Format
    ```

4.  Redémarrez le service Rsyslog.

Voici comment interpréter cette ligne :
– *.* : signifie qu’on doit envoyer tous les logs Syslog de la machine Linux vers Graylog.
– @ : indique que le transport est effectué en UDP. Il convient de préciser "@@" pour
basculer en TCP.
– 172.16.0.6:12514 : indique l’adresse du serveur Graylog, ainsi que le port sur lequel on
envoie les logs (correspondant à l'Input).
– RSYSLOG_SyslogProtocol23Format : correspond au format des messages que l’on veut
envoyer à Graylog.
· Enregistrez le fichier et redémarrez le service Rsyslog. Les premiers messages devraient
arriver sur votre serveur Graylog !


## ⚠️ ATTENTION, PROBLEME SERVEUR NTP POISON

Pour régler ce problème :

Sur **Stormshield**, allez dans **Monitoring -> Tous les journaux**. Recherchez la ligne de log qui bloque le serveur ntp de rennes avec le message : **NTP : possible attaque de type poisoning**.

* Faites un **Clic droit** sur la ligne.
* Sélectionnez **Accéder à la configuration des alarmes**.
* Recherchez la règle d'alarme pour **NTP : possible attaque de type poisoning**.
* **Autoriser ce message**.

# Centraliser les logs : logs Windows

### 1. Configuration de Graylog pour recevoir les logs

| Composant | Type | Nom | Paramètres Clés |
| :--- | :--- | :--- | :--- |
| **Input** | GELF UDP | `Win_Log_TVC` | Port : **12201** |
| **Index** | N/A | `index_win_log` | **System / Indices > Create index set** |
| **Stream** | N/A | `stream_win_log` | Index Set : **`index_win_log`** ; Cochez : **`Remove matches from 'default stream'`** |

**Liaison Stream/Input :** Sur le Stream `stream_win_log`, accédez à **Manage Rules** > **Add Stream Rule** : Type **`match input`** et sélectionnez l'Input **`Win_Log_TVC`**.

### 2. Configuration de NXLog pour l'envoi des logs à Graylog

1.  Installez et paramétrez l'agent **NXLog Community Edition** sur le serveur `SRV-WIN1` (fichier `nxlog-ce-3.2.2329.msi`).
2.  Modifiez le fichier de configuration `C:\Program Files\nxlog\conf\nxlog.conf` en ajoutant les lignes suivantes à la fin :

```xml
# Récupérer les journaux de l'observateur d'événements
<Input in>
    Module im_msvistalog
    <QueryXML>
        <QueryList>
            <Query Id='1'>
                <Select Path='Security'>*</Select>
            </Query>
        </QueryList>
    </QueryXML>
</Input>

# Déclarer le serveur Graylog (selon input)
<Extension gelf>
    Module xm_gelf
</Extension>
<Output graylog_udp>
    Module om_udp
    Host 172.16.0.6
    Port 12201
    OutputType GELF_UDP
</Output>

# Routage des flux in vers out
<Route 1>
    Path in => graylog_udp
</Route>
```
Sauvegardez les changements et redémarrez le service NXLog (en console PowerShell Admin) :

```powershell
Restart-Service nxlog
```

### 3. Recevoir des logs dans Graylog

1. Cliquez sur "Search" dans le menu de Graylog pour vérifier l'arrivée des journaux.

2. Pour filtrer les événements (ex: tentatives de connexion), utilisez :

```plaintext
EventID:4776 OR EventID:4771
```

3. GPO d'audit : Créez la GPO « audit » sur le domaine de contrôle pour générer ces événements.

4. Ouvrez une console CMD et forcez l’application de cette GPO :

```powershell
gupdate /force
```

### 4. Génération de logs d’authentification avec une Kali (Kerbrute)

1. Dans la Kali, téléchargez Kerbrute à l’adresse `https://github.com/ropnop/kerbrute/releases/tag/v1.0.3`. Renommez le fichier `kerbrute` et donnez à tous les utilisateurs les droits d’exécution :

```bash
chmod 777 kerbrute
```

2. Pour déterminer un mot de passe de l’utilisateur par défaut de Windows AD, tapez cette commande en console :

```bash
kerbrute bruteuser -d sodecaf.local --dc 172.16.0.1 /usr/share/sqlmap/data/txt/wordlist.txt administrateur 
```

3. Puis ouvrez une ouverture du bureau à distance Windows depuis la Kali avec le mot de passe trouvé :

```bash
xfreerdp3 /u:"sodecal.local\Administrateur" /p:"Rootsio2017" /v:172.16.0.1 /cert:ignore
```

4. Observez les logs. Faites un filtre avec `EventID : 4776` (NTLM bruteforce) ou `EventID : 4771` (Password spraying bruteforce).


## 4. 🛡️ Centralisation des Logs Stormshield

### 4.1. Configuration de l’envoi des logs Stormshield vers Graylog

1.  Dans le menu **Configuration > Système > Configuration** sur Stormshield, ajoutez le serveur NTP de l’université de Rennes 2 (`ntp.univ-rennes2.fr`).
2.  Dans le menu **Configuration > Notifications > Traces – Syslog IPFIX > Syslog**, configurez le Stormshield pour qu’il envoie des logs au format syslog au serveur Graylog.
3.  Utilisez le port personnalisé **UDP `1514`**.

### 4.2. Configuration de la récupération et l’exploitation des logs sur Graylog

| Composant | Type | Nom | Paramètres Clés |
| :--- | :--- | :--- | :--- |
| **Input** | Syslog UDP | `Stormshield_UDP` | Port : **1514** |
| **Index** | N/A | `Index_Stormshield` | Utiliser un template par défaut. |
| **Stream** | N/A | `Stormshield` | Index Set : **`Index_Stormshield`** |

**Liaison Stream/Input :** Sur le Stream `Stormshield`, **Manage Rules** > **Add Stream Rule** : Type **`match input`** et sélectionnez **`Stormshield_UDP`**.

### 4.3. Utilisation d’un Modèle (Content Pack)

Vous utiliserez un Content Pack pour importer, parser et créer un dashboard pour les logs Stormshield.

1.  Consultez la documentation : `https://github.com/s0p4L1n3/Graylog_Content_Pack_Stormshield_Firewall/blob/main/README.md`.
2.  Modifiez le fichier JSON téléchargé en remplaçant `firewall.lab.lan` par l'identifiant de votre pare-feu : **`VMSNSX09K0639A9`**.
3.  Importez et installez ce Content Pack sur Graylog.

---

## 5. ⚠️ Annexe : Correction NTP Poisoning

### 5.1. Résolution du Blocage Serveur NTP

Pour régler le problème **NTP : possible attaque de type poisoning** sur Stormshield :

* Sur **Stormshield**, allez dans **Monitoring -> Tous les journaux**.
* Recherchez la ligne de log qui bloque le serveur NTP.
* Faites un **Clic droit** sur la ligne, puis sélectionnez **Accéder à la configuration des alarmes**.
* Recherchez la règle d'alarme pour **NTP : possible attaque de type poisoning**.
* **Autoriser ce message**.

# 📧 Centraliser les logs : alertes par email

### 1. Configuration du Compte Google (Mot de passe d'application)

1.  Connectez-vous à votre compte Gmail.
2.  Cliquez sur votre photo de profil, puis sur **`Gérer votre compte Google`**.
3.  Allez dans la section **`Sécurité`** (ou `Sécurité et connexion`).
4.  Recherchez **`Mots de passe des applications`** (vous devrez peut-être vous reconnecter).
5.  Créez un nouveau mot de passe d'application, donnez-lui le nom **`graylog`**.
6.  **Copiez le mot de passe généré** et collez-le dans un bloc-notes en **supprimant tous les espaces**.

### 2. Configuration du Serveur Graylog

1.  Éditez le fichier de configuration Graylog sur la machine Graylog :

```bash
nano /etc/graylog/server/server.conf
```

2.  **Éditez la partie `Email transport`** en décommentant les lignes et en modifiant les valeurs suivantes (remplacez `adresse mail` par votre adresse Gmail et `secret` par le mot de passe d'application généré à l'étape 1) :

```ini
transport_email_enabled = true
transport_email_hostname = smtp.gmail.com
transport_email_port = 587
transport_email_use_auth = true
transport_email_auth_username = adresse mail
transport_email_auth_password = secret
transport_email_from_email = adresse mail
transport_email_socket_connection_timeout = 10s
transport_email_socket_timeout = 10s
```

3.  Plus loin, décommentez ces 2 lignes pour activer TLS et définir l'URL de l'interface :

```ini
transport_email_use_tls = true

transport_email_web_interface_url = [http://172.16.0.6:9000](http://172.16.0.6:9000)
```

4.  Redémarrez le service Graylog :

```bash
systemctl restart graylog-server.service
```

### 3. Création de la Règle Stormshield pour SMTP

Créez une nouvelle règle de **filtering** dans la **Security Policy** du Stormshield pour laisser passer le trafic SMTP chiffré (`submission` est le port 587).

| Status | Action | Source | Destination | Dest. Port |
| :---: | :---: | :---: | :---: | :---: |
| ON | PASS | ANY | ANY | submission |

### 4. Test de Connexion SMTP

1.  Testez la connexion au serveur SMTP avec `telnet` depuis la machine Graylog :

```bash
telnet smtp.gmail.com 587
```

2.  Le résultat attendu est : **`Connected to smtp.gmail.com`**.

### 5. Installation et Configuration de `s-nail`

1.  Installez `s-nail` sur Graylog :

```bash
apt install s-nail
```

2.  Créez le fichier de configuration `~/.mailrc` pour l'envoi d'e-mails de test (remplacez les valeurs entre guillemets) :

```bash
cat > ~/.mailrc <<EOF
set mta=smtp://smtp.gmail.com:587
set smtp-use-starttls
set smtp-auth=login
set smtp-auth-user="votre_mail@gmail.com"
set smtp-auth-password="mot_de_passe_de_l’application"
set from="votre_mail@gmail.com"
EOF
```

3. Testez l'envoi d'un mail :

```bash
echo "Test d’envoi depuis le serveur Graylog" | s-nail -s "Test SMTP" votre_mail@gmail.com
```

4. Vous devriez reçevoir un mail `Test SMTP`

# 📧 Centraliser les logs : alertes par email

### 1. Configuration du Compte Google (Mot de passe d'application)

1.  Aller sur son compte gmail, cliquer sur sa photo de profil, aller dans **`Gérer votre compte Google`** puis dans **`Sécurité`** (ou `Sécurité et connexion`).
2.  Rechercher **`Mots de passe des applications`** (généralement dans la section "Comment vous connecter à Google").
3.  Mettre le nom de l'application **`graylog`** et **copier le mot de passe** généré dans un bloc-notes en enlevant les espaces.

### 2. Configuration du Serveur Graylog (Email transport)

1.  Sur la machine Graylog, éditer le fichier de configuration :

    ```bash
    nano /etc/graylog/server/server.conf
    ```

2.  **Décommenter et modifier** la partie `Email transport` :

    ```ini
    transport_email_enabled = true
    transport_email_hostname = smtp.gmail.com
    transport_email_port = 587
    transport_email_use_auth = true
    transport_email_auth_username = adresse mail
    transport_email_auth_password = secret
    transport_email_from_email = adresse mail
    transport_email_socket_connection_timeout = 10s
    transport_email_socket_timeout = 10s
    ```
    *(Remplacez `adresse mail` par votre adresse Gmail et `secret` par le mot de passe d'application.)*

3.  Décommenter les lignes pour **TLS** et l'**URL de l'interface web** :

    ```ini
    transport_email_use_tls = true

    transport_email_web_interface_url = [http://172.16.0.6:9000](http://172.16.0.6:9000)
    ```

4.  Redémarrer le service Graylog :

    ```bash
    systemctl restart graylog-server.service
    ```

### 3. Création de la Règle Stormshield pour SMTP

Créez une nouvelle règle de **filtering** dans la **Security Policy** du Stormshield :

| Status | Action | Source | Destination | Dest. Port |
| :---: | :---: | :---: | :---: | :---: |
| ON | PASS | ANY | ANY | submission |

### 4. Test de Connexion SMTP

1.  Tester la connexion au serveur SMTP avec `telnet` :

    ```bash
    telnet smtp.gmail.com 587
    ```

2.  Le résultat doit être : **`Connected to smtp.gmail.com`**.

### 5. Installation et Configuration de `s-nail`

1.  Installer `s-nail` sur Graylog :

    ```bash
    apt install s-nail
    ```

2.  Créer un fichier de configuration pour les tests d'envoi :

    ```bash
    cat > ~/.mailrc <<EOF
    set mta=smtp://smtp.gmail.com:587
    set smtp-use-starttls
    set smtp-auth=login
    set smtp-auth-user="votre_mail@gmail.com"
    set smtp-auth-password="mot_de_passe_de_l’application"
    set from="votre_mail@gmail.com"
    EOF
    ```

---

## 5. 📧 Configuration de l'Alerte SSH Échouée (Suite)

### 5.1. A. Créer un Nouveau Stream pour les Erreurs SSH

1.  Cliquez sur **"Streams"** puis créez un nouveau Stream, nommez-le par exemple **"Erreurs de connexion SSH"**.
2.  Sélectionnez l'index approprié (ex: **"Linux Index"**).

3.  **Définir les Règles du Stream :** Cliquez sur **"More"**, puis **"Manage Rules"** et **"Add stream rule"**.

| Type | Champ | Valeur |
| :--- | :--- | :--- |
| **Message must contain** | `message` | `Failed password` |
| **Message must contain** | `application_name` | `sshd` |

4.  Validez avec **"I'm done!"** et cliquez sur le bouton **"Paused"** pour rendre le Stream **actif**.

### 5.2. B. Créer un Nouveau Type de Notification

1.  Dans le menu **"Alerts"**, allez dans l'onglet **"Notifications"** et cliquez sur **"Create notification"**.
2.  Donnez un nom (ex: **"Notification - Erreur connexion SSH - Linux"**) et choisissez le type **"Email Notification"**.
3.  Définissez le(s) destinataire(s) via **"Email recipient(s)"**.
4.  Cliquez sur **"Execute test notification"** pour valider la configuration e-mail.

### 5.3. C. Créer une Nouvelle Alerte (Event Definition)

1.  Dans la section **"Alerts"**, allez dans **"Event Definitions"** et cliquez sur **"Create event definition"**.
2.  Nommez l'alerte (ex: **"Erreur connexion SSH - Linux"**).
3.  À l'étape **"Condition"**, choisissez **"Filter & Aggregation"**.

4.  **Configuration du Filtre :**

| Paramètre | Valeur |
| :--- | :--- |
| **Search query** | `Failed password` |
| **Streams** | **"Erreur de connexion SSH"** |
| **Search within the last** | 1 minute |
| **Execute search every** | 1 minute |

5.  Passez l'étape **"Fields"**. À l'étape **"Notifications"**, sélectionnez le modèle de notification créé (ex: "Notification - Erreur connexion SSH - Linux") et **"Add notification"**.
6.  Cliquez sur **"Summary"** et validez avec **"Create event definition"**.

### 5.4. D. Tester l'Alerte

1.  Simulez une connexion SSH en échec sur un serveur Linux pour déclencher l'alerte.
2.  Un e-mail doit arriver dans la minute, contenant le lien **"Alert Replay"** pour l'analyse dans Graylog.

