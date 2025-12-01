# Installation de Graylog sur une Debian 12

Configurer l'IP de la machine Debian et modifier son nom

```bash
nano /etc/network/interfaces
```


Pour appliquer le fuseau horaire Europe/Paris sur votre machine Debian:

```bash
timedatectl set-timezone Europe/Paris
``` 

Nous allons synchroniser l’horloge de nos serveurs avec un serveur de temps de l’université de Rennes2 : ntp.univ-
rennes2.fr. En cas de défaillance de ce serveur de temps, nous utiliserons des serveurs du pool.ntp.org.

Éditez le fichier /etc/systemd/timesyncd.conf et paramétrez le serveur de temps utilisé :

```bash
[Time]
NTP=ntp.univ-rennes2.fr
FallbackNTP=0.debian.pool.ntp.org 1.debian.pool.ntp.org 2.debian.pool.ntp.org 3.debian.pool.ntp.org
```

Il reste à définir le service NTP actif :

```bash
timedatectl set-ntp true
```

Vérifiez alors que la synchronisation fonctionne en utilisant les commandes timedatectl et timedatectl

```bash
timesync-status ... Ceci n’est pas immédiat et peut prendre plusieurs minutes...
timedatectl
timedatectl timesync-status
```

mettre à jour la machine 

```bash
apt update 
apt upgrade -y
```

Installer les paquets nécessaires pour installer Graylog 

```bash
apt-get install curl lsb-release ca-certificates gnupg2 pwgen

curl -fsSL https://www.mongodb.org/static/pgp/server-6.0.asc | gpg -o /usr/share/keyrings/mongodb-server-6.0.gpg --dearmor

echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg] http://repo.mongodb.org/apt/debian bullseye/mongodb-org/6.0 main" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list

apt update

wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2.24_amd64.deb

dpkg -i libssl1.1_1.1.1f-1ubuntu2.23_amd64.deb

apt-get install -y mongodb-org

apt update
``` 

Ensuite, relancez le service MongoDB et activez son démarrage automatique au lancement du serveur Debian.

```bash
systemctl daemon-reload
systemctl enable mongod.service
systemctl restart mongod.service
systemctl --type=service --state=active | grep mongod
```

Nous allons passer à l'installation d'OpenSearch sur le serveur. La commande suivante permet d’ajouter la clé de signature pour les paquets OpenSearch :

```bash
curl -o- https://artifacts.opensearch.org/publickeys/opensearch.pgp | gpg --dearmor --batch --yes -o /usr/share/keyrings/opensearch-keyring

echo "deb [signed-by=/usr/share/keyrings/opensearch-keyring] https://artifacts.opensearch.org/releases/bundle/opensearch/2.x/apt stable main" | tee /etc/apt/sources.list.d/opensearch-2.x.list

apt-get update
```

Puis, installez OpenSearch en prenant soin de définir le mot de passe par défaut pour le compte Admin de votre instance. Ici, le mot de passe est "Rootsio2017!", mais remplacez cette valeur par un mot de passe robuste. Évitez les mots de passe faibles du style "P@ssword123" et utilisez au moins 8 caractères avec au moins un caractère de chaque type (minuscule, majuscule, chiffre et caractère spécial), sinon il y aura une erreur à la fin de l'installation. C'est un prérequis depuis OpenSearch 2.12.

```bash
env OPENSEARCH_INITIAL_ADMIN_PASSWORD=Rootsio2017! apt-get install opensearch
```

Quand c'est terminé, prenez le temps d'effectuer la configuration minimale. Ouvrez le fichier de configuration au format YAML :

```bash
nano /etc/opensearch/opensearch.yml
```

```yml
cluster.name: graylog
node.name: ${HOSTNAME}
path.data: /var/lib/opensearch
path.logs: /var/log/opensearch
discovery.type: single-node
network.host: 127.0.0.1
action.auto_create_index: false
plugins.security.disabled: true
```

Vous devez configurer Java Virtual Machine utilisé par OpenSearch afin d'ajuster la quantité de mémoire que peut utiliser ce service. Éditez le fichier de configuration suivant :

```bash
nano /etc/opensearch/jvm.options
```

Avec la configuration déployée ici, OpenSearch démarrera avec une mémoire allouée de 2 Go et pourra atteindre jusqu'à 2 Go, il n'y aura donc pas de variation de mémoire pendant le fonctionnement. Ici, la configuration tient compte du fait que la machine virtuelle dispose d'un total de 4 Go de RAM. Les deux paramètres doivent avoir la même valeur. Ceci implique de remplacer ces lignes :

```ini
-Xms1g
-Xmx1g
``` 

Par :

```ini
-Xms2g
-Xmx2g
``` 

Enfin, activez le démarrage automatique d'OpenSearch et lancez le service associé.

```bash
systemctl daemon-reload
systemctl enable opensearch
systemctl restart opensearch
```

Si vous affichez l'état de votre système, vous devriez voir un processus Java avec 4 Go de RAM et comme nom Opensearch.

```bash
top
```

Pour effectuer l'installation de Graylog 6.1 dans sa dernière version, exécutez les 4 commandes suivantes afin de télécharger et d'installer Graylog Server :

```bash
wget https://packages.graylog2.org/repo/packages/graylog-6.1-repository_latest.deb
dpkg -i graylog-6.1-repository_latest.deb
apt-get update
apt-get install graylog-server
```

Quand c'est fait, nous devons apporter des modifications à la configuration de Graylog avant de chercher à le lancer.

Commençons par configurer ces deux options :

    password_secret : ce paramètre sert à définir une clé utilisée par Graylog pour sécuriser le stockage des mots de passe utilisateurs (dans l'esprit d'une clé de salage). Cette clé doit être unique et aléatoire.
    root_password_sha2 : ce paramètre correspond au mot de passe de l’administrateur par défaut dans Graylog. Il est stocké sous forme d'un hash SHA-256.

Nous allons commencer par générer une clé de 96 caractères pour le paramètre password_secret :

```bash
pwgen -N 1 -s 96
```

Copiez la valeur retournée, puis ouvrez le fichier de configuration de Graylog :

```bash
nano /etc/graylog/server/server.conf
```

Collez la clé au niveau du paramètre password_secret

Enregistrez et fermez le fichier.

Ensuite, vous devez définir le mot de passe du compte "admin" créé par défaut. Dans le fichier de configuration, c'est le hash du mot de passe qui doit être stocké, ce qui implique de le calculer. L'exemple ci-dessous permet d'obtenir le hash du mot de passe "Rootsio2017" : adaptez la valeur avec votre mot de passe.

```bash
echo -n "Rootsio2017" | shasum -a 256
```

Copiez la valeur obtenue en sortie (sans le tiret en bout de ligne).

Ouvrez de nouveau le fichier de configuration de Graylog :

```bash
nano /etc/graylog/server/server.conf
```

Collez la valeur au niveau de l'option root_password_sha2 

Profitez d'être dans le fichier de configuration pour configurer l'option nommée "http_bind_address". Indiquez "0.0.0.0:9000" pour que l'interface web de Graylog soit accessible sur le port 9000, via n'importe quelle adresse IP du serveur.

```bash
http_bind_address = 0.0.0.0:9000
```

Puis, configurez l'option "elasticsearch_hosts" avec la valeur "http://127.0.0.1:9200" pour déclarer notre instance locale OpenSearch. Ceci est nécessaire, car nous n'utilisons pas de Graylog Data Node. Et sans cette option, il ne sera pas possible d'aller plus loin...

```bash
elasticsearch_hosts =http://127.0.0.1:9200
```

Modifier root_timezone, décommentez la ligne et mettre `Europe/Paris`

```bash
root_timezone = Europe/Paris
```

Enregistrez et fermez le fichier.

Cette commande active Graylog pour qu'il démarre automatiquement au prochain démarrage et elle lance immédiatement le serveur Graylog.

```bash
systemctl enable --now graylog-server
```

Accéder à l'interface web de graylog http://172.16.0.6:9000 (172.16.0.6 étant l'IP de ma machine Debian 12)

login : admin
MDP : Rootsio2017

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

# Centraliser les logs : alertes par email

Pour commencer, aller sur son compte gmail, cliquer sur sa photo de profil, aller dans `Gérer votre compte Google` puis dans `Sécurité et connexion`, rechercher dans la barre `Mots de passe des applications`, mettez le nom de l'application `graylog` et copier le mdp dans un bloc notes en enlevant les espaces.

Sur la machine Graylog, éditer le fichier de configuration graylog

```bash
nano /etc/graylog/server/server.conf
```

éditer la partie `Email transport`

décommenter toute la partie email transport et modifier :

```ini
transport_email_enabled = true
transport_email_hostname = smtp@gmail.com
transport_email_port = 587
transport_email_use_auth = true
transport_email_auth_username = adresse mail
transport_email_auth_password = secret
transport_email_from_email = adresse mail
transport_email_socket_connection_timeout = 10s
transport_email_socket_timeout = 10s
```

Plus loin, décommenter ces 2 lignes 

```ini
transport_email_use_tls = true

transport_email_web_interface_url = http://172.16.0.6:9000
```

redémarrer le service graylog 

```bash
systemctl restart graylog-server.service
```

Sur Stormshield, créer une nouvelle règle pour laisser passer SMTP 

Dans security policy, créer une règle de filtering


| Status | Action | Source | Destination | Dest. Port |
| :---: | :---: | :---: | :---: | :---: |
| ON | PASS | ANY | ANY | submission |


tester la connexion au serveur SMTP avec telnet

```bash
telnet smtp.gmail.com 587
```

Il devrait renvoyer `Connected to smtp.gmail.com`

Installer ensuite s-nail sur Graylog

```bash
apt install s-nail
```

Puis créer un fichier de configuration 

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



