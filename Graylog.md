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

# Importer des logs 

Avant l’import d’un fichier logs de test, Il y a trois étapes à accomplir :
la création d'un Input pour créer un point d'entrée permettant pour l’arrivée des logs ;
la création d'un nouvel index pour stocker et indexer tous les journaux ;
la création d'un Stream pour router les journaux reçus par Graylog vers le nouvel Index.

Création d’un « input » dans Graylog
Sous l’interface web de Graylog, allez dans le menu System > Inputs.


Choisissez Raw/Plaintext TCP puis Launch new input.
Entrez le titre Graylog_TCP_test_Linux et laissez les autres paramètres par défaut :

Validez. Graylog est maintenant en écoute sur son port 5555.


Création d’un « index» dans Graylog
Cela permet de ne pas mélanger ces logs d'exercice avec d'autres.
Sur Graylog, cliquez sur System > Indices > Create index set. Choisissez le template 7-days hot.
Entrez les éléments ci-contre pour identifier ces logs :

Création des Streams (flux de logs)
L’objectif est de créer un flux de logs correspondant à l’input créée.

Allez dans Streams → Create Stream. Entrez un nom et retrouvez l’index créé précédemment :


Sur la ligne du Stream créé, cliquez sur More puis Manage rules. Choisissez le type "match input" et sélectionnez l'Input Graylog_TCP_test_Linux. Validez avec le bouton "Create Rule".



Ainsi, tous les messages à destination de notre nouvel Input seront envoyés dans l'Index web-test.

Import des logs
A partir de la machine physique Windows 11, nous allons envoyer le fichier de logs au serveur Graylog avec la commande ncat en utilisant un script. Copiez-collez le script ci-dessous dans un fichier script.bat. Enregistrez-le dans le dossier où se situe le fichier logs.txt. Placez vous en console cmd et exécutez le.

@echo off
set GRAYLOG_HOST=172.16.0.6
set GRAYLOG_PORT=5555

for /f "delims=" %%l in (logs.txt) do (
    echo %%l | "C:\Program Files (x86)\Nmap\ncat.exe" %GRAYLOG_HOST% %GRAYLOG_PORT%
)

Sur Graylog, sur le Stream web-test, vous devez voir des logs apparaître. Lors de l’import, ne tenez pas compte du warning éventuel : libnsock ssl_init_helper(): OpenSSL legacy provider failed to load.

# Centraliser les logs : logs Linux

1. Configuration de Graylog pour recevoir les logs
Avant de pouvoir recevoir des logs depuis un équipement réseau, Vous allez devoir ouvrir une porte
d’entrée (input) sur Graylog. Ensuite, pour bien organiser les données, on crée un index dédié
(comme un dossier thématique) et un flux (stream) pour diriger les messages vers ce bon dossier.

· Pour paramétrer le graylog, dans le menu system, créez un input : menu System/inputs >
Input.

· Choisissez dans le menu déroulant Syslog UDP et cliquez sur Launch new input.

· Nommez votre `Input Graylog_UDP_rsyslog_input`, choisissez le numéro de port 12514, conservez tout le message de log en cochant `store full message ?`, réglez l’heure en séléctionnant la Time Zone `UTC+01:00-Europe/Paris` et le reste laissez par défaut.

· Une fois l’input fait, créez un index pour le stream (flux de log) dans System / Indices nommé `linux-index`

Puis il faut créer le stream dédié : nommé `linux-stream` et mettre `linux-index` dans index Set et cocher `Remove matches from 'Default Stream'`

· Vous devez maintenant lier votre stream à l’Input, pour cela cliquez sur more et rajoutez
une règle en cliquant sur manage Rules , puis add stream Rule, le type en `match input` et seléctionner l'input créé `Graylog_UDP_rsyslog_input`

Une fois le service démarré et fonctionnel, nous pouvons terminer notre configuration sur le serveur
web

Installer rsyslog sur le serveur web 

```bash
apt install rsyslog
```

Puis créer un fichier dans rsyslog.d

```bash
nano /etc/rsyslog.d/1-Linux-graylog
```

et insérer cette ligne : 

```ini
*.* @172.16.0.6:12514;RSYSLOG_SyslogProtocol23Format
```

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


## ATTENTION, PROBLEME SERVEUR NTP POISON QUI BLOQUE LE SERVEUR DE TEMPS

Pour régler ça :

sur stormshield, aller dans monitoring -> Tous les journaux -> rechercher la ligne de log qui bloque le serveur ntp de rennes avec comme message : NTP : possible attaque de type poisoning -> clic droit -> Accéder à la configuration des alarmes -> rechercher NTP : possible attaque de type poisoning -> Autoriser ce message

# Centraliser les logs : logs Windows

1. Configuration de Graylog pour recevoir les logs
Pour paramétrer le graylog, il est nécessaire de créer un input, un index et un stream.

· Nous allons commencer par créer un input dans Graylog pour les logs de Windows. Il faut
aller dans System/inputs, choisissez le protocole GELF UDP et nommer le Win_Log_TVC.

· Créez l’index et nommer la index_win_log, lui mettre une description.

Enfin, créer le stream nommé stream_win_log, mettre index_win_log dans Index Set et cocher Remove matches from 'default stream'
 
Pour terminer, manage rules du stream et select an input prendre win_log_tvc et add stream rule Type match input et seléctionner win_log_tvc.

2. Configuration de Nxlog pour envoyer les logs à graylog et les analyser
Par défaut, Windows n'est pas capable d'envoyer ses journaux vers un serveur Graylog (ou
équivalent) puisque les fonctions de transferts de journaux sont très limitées. Pour répondre à cette
problématique, nous allons utiliser l'agent NXLog dans sa version communautaire. Il va
permettre de capturer les journaux sur la machine Windows afin de les router vers le serveur
Graylog.

· En vous aidant du tutoriel à https://www.it-connect.fr/envoyer-les-logs-windows-vers-
graylog-avec-nxlog/, installez et paramétrez sur le serveur SRV-WIN1, nxlog community

(fichier nxlog-ce-3.2.2329.msi).

B3-Act6-TP2e – Centraliser les logs : logs Windows page 3/6
· Ouvrez une console en admin PowerShell ISE. Configurez le fichier C :\Program
Files\nxlog\conf\nxlog.conf en rajoutant ces lignes à la fin du programme :
# Récupérer les journaux de l'observateur
d'événements
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
Quelques explications s'imposent pour vous aider à comprendre :
– im_msvistalog : il s'agit du module déclaré comme entrée (Input) pour récupérer les
journaux dans l'Observateur d'événements de Windows, compatible à partir de Windows
Server 2008 et Windows Vista. Il est toujours compatible avec les dernières versions, à
savoir Windows 11 et Windows Server 2025. Pour les versions antérieures à Windows
Server 2008, utilisez le module "im_mseventlog".
– om_udp : il s'agit du module déclaré comme sortie (Output graylog_udp). Dans ce bloc,
vous devez modifier l'adresse IP, car elle correspond au serveur Graylog (172.16.0.6) et
éventuellement le port. Nous utilisons le type de sortie "GELF_UDP" pour rester cohérent
vis-à-vis de l'Input déclaré dans Graylog.
– Route 1 : il s'agit d'une règle « de routage » dans NXLog pour prendre ce qui correspond à
l'Input "in" (les logs Windows) et les envoyer vers la sortie "graylog_udp", à savoir notre
Graylog.
– <Select Path='Security'>*</Select> : sert à modifier l'Input dans la configuration de
NXLog pour transmettre à Graylog uniquement les événements du journal "Sécurité"

B3-Act6-TP2e – Centraliser les logs : logs Windows page 4/6
· Sauvegardez les changements et redémarrez le service NXLog à partir d'une console
PowerShell ouverte en tant qu'administrateur (ou via la console Services) : Restart-Service
nxlog
Si votre configuration ne fonctionne pas, ouvrez le fichier de logs de NXLog dans C:\Program
Files\nxlog\data\nxlog.log

3. Recevoir des logs dans graylog
Suite à la configuration de Graylog et de l'agent NXLog sur la machine Windows, les journaux
doivent désormais être envoyés vers Graylog.
· Pour le vérifier, cliquez simplement sur "Search" dans le menu de Graylog.
Vous devriez voir de premiers journaux arriver, ce qui aura pour effet de faire un pic de logs. Je
vous recommande de cliquer sur le bouton mis en évidence sur l'image ci-dessous pour rafraîchir
la liste automatiquement toutes les 5 secondes (par défaut).

Si vous cliquez sur un log dans la liste, vous pouvez visualiser son contenu. Cela revient à consulter
le journal à partir de l'Observateur d'événements de Windows.
Les journaux étant stockés et indexés dans Graylog, la puissance de l'outil réside dans sa fonction
de recherche. Vous pouvez rédiger un filtre dans la zone de saisie située à droite de la loupe.
Par exemple, voici comment filtrer les événements pour afficher uniquement ceux dont l'ID
est 4776 ou 4771. Ceci permet d'identifier les tentatives de connexion infructueuses sur un
ou plusieurs serveurs. Pour que ces événements soient générés, vous devez ajuster la stratégie
d'audit de Windows.

B3-Act6-TP2e – Centraliser les logs : logs Windows page 5/6

· Pour cela créez la GPO « audit » suivante sur le domaine de contrôle :

· Ouvrez une console CMD et forcez l’application de cette gpo : gpupdate /force puis
vérifiez : gpresult /R

4. Génération de logs d’authentification avec une kali
· Démarrez une VM Kali Linux dans le LAN.
Pour générer des tentatives de connexion, nous allons pour cela utiliser Kerbrute :

Kerbrute est un outil d’énumération et d’attaque Kerberos, utilisé principalement dans des audits
de sécurité Active Directory. Il est écrit en GO et est très rapide car il ne dépend pas de
l’authentification NTLM ou LDAP, mais interagit directement avec le protocole Kerberos (port
88/UDP).

B3-Act6-TP2e – Centraliser les logs : logs Windows page 6/6
Kerberos est un protocole d’authentification basé sur des tickets chiffrés permettant de prouver
l’identité d’un utilisateur sans envoyer son mot de passe en clair sur le réseau :
– Un client demande un TGT (Ticket Granting Ticket) au contrôleur de domaine (KDC) en
prouvant son identité via la pré-authentification.
– Avec ce TGT, il demande ensuite un ticket de service pour accéder à une ressource (serveur,
partage, application...).
– Les tickets sont chiffrés à l’aide de clés secrètes afin d’empêcher l’usurpation d’identité.
– Kerberos permet une authentification sécurisée et centralisée dans les environnements
Windows (Active Directory).
Kerbrute n’effectue que la première étape, la demande du ticket au contrôleur de domaine. Il ne
demande ensuite aucun service.
· Dans la Kali, téléchargez Kerbrute à l’adresse
https://github.com/ropnop/kerbrute/releases/tag/v1.0.3. Rennomez le fichier kerbrute et
donnez à tous les utilisateurs les droits d’exécution.

```bash
chmod 777 kerbrute
```

· Pour déterminer un mot de passe de l’utilisateur par défaut de Windows AD, nous allez taper
cette commande en console :

```bash
kerbrute bruteuser -d sodecaf.local --dc 172.16.0.1 /usr/share/sqlmap/data/txt/wordlist.txt administrateur 
```

· Puis nous allons ouvrir avec le mot de passe trouvé, une ouverture du bureau à distance
Windows depuis la kali :

xfreerdp3 /u:"sodecal.local\Administrateur" /p:"Rootsio2017" /v:172.16.0.1 /cert:ignore

· Observez les logs. Faites un filtre avec EventID : 4776 (NTLM bruteforce) ou EventID : 4771
(Password spraying bruteforce).

# Centraliser les logs : logs Stormshield

1. L’envoi des logs Stormshield vers Graylog
· Dans le menu Configuration > Système > Configuration, ajoutez le serveur NTP de
l’université de Rennes 2 (ntp.univ-rennes2.fr).
· Dans le menu Configuration > Notifications > Traces – Syslog IPFIX > Syslog, configurez le
Stormshield afin qu’ils envoient des logs au format syslog au serveur Graylog. Vous utiliserez
le port personnalisé UDP 1514.

2. La récupération et l’exploitation des log sur Graylog
· Créez une nouvelle « input » Stormshield_UDP qui écoute sur le port UDP 1514, en utilisant
le protocole syslog.
· Créez un index Index_Stormshield utilisant un template par défaut.
· Créez enfin un nouveau « Streams » Stormshield qui utilise cet index et qui répertorie tous
les logs qui « match » avec l’input Stormshield_UDP.
Les logs du Stormshield apparaissent dans le Stream créé :

B3-Act6-TP2f – Centraliser les logs : logs Stormshield page 3/3

3. Utilisation d’un modèle
Vous allez utiliser un modèle, appelé « content pack » sur Graylog, afin d’importer, de parser et de
créer un dashboard pour les logs du Stormshield.
· Utilisez le site
https://github.com/s0p4L1n3/Graylog_Content_Pack_Stormshield_Firewall/blob/main/REA
DME.md pour la mise en place de ce content pack. Modifiez le nom du pare-feu dans le
fichier json téléchargé, en remplaçant firewall.lab.lan par VMSNSX09K0639A9.
· Importez ce content pack sur Graylog et installez-le. Un nouvel Input, un nouveau Stream
et un nouveau Dashboard sont créés.

4. Analyse des journaux
· Revenez l’activité sur la mise en place de l’IPS du Stormshield. Retrouvez sur Graylog les
logs correspondants aux différentes attaques menées avec la Kali. Si besoin, modifiez le
Dashboard.

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



|ON   |   PASS    |    ANY  |   ANY   |  submission|



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

