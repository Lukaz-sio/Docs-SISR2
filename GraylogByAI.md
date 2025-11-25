# Installation et Configuration de Graylog 6.1

## Prérequis

- Serveur Debian 12
- 4 cœurs CPU minimum
- 8 GB de RAM minimum
- 50 GB d'espace disque

## Architecture du Système

Graylog 6.1 repose sur trois composants principaux :

| Composant | Version | Port | Rôle |
|-----------|---------|------|------|
| Graylog Server | 6.1 | 9000 (HTTP) | Application principale et interface web |
| MongoDB | 6.0 | 27017 | Base de données de configuration |
| OpenSearch | 2.x | 9200/9300 | Moteur de recherche et stockage des logs |

---

## Installation sur Debian 12

### 1. Mise à jour du système

```bash
apt update
apt upgrade -y
```

### 2. Installation des dépendances

```bash
apt install -y apt-transport-https gnupg2 curl openjdk-17-jre-headless pwgen
```

### 3. Installation de MongoDB 6.0

```bash
curl -fsSL https://www.mongodb.org/static/pgp/server-6.0.asc | apt-key add -
echo "deb http://repo.mongodb.org/apt/debian bullseye/mongodb-org/6.0 main" > /etc/apt/sources.list.d/mongodb.list
apt update
apt install -y mongodb-org
systemctl enable mongod
systemctl start mongod
```

### 4. Installation d'OpenSearch 2.x

```bash
curl -fsSL https://artifacts.opensearch.org/publickeys/opensearch.pgp | apt-key add -
echo "deb https://artifacts.opensearch.org/releases/bundle/opensearch/2.x/apt stable main" > /etc/apt/sources.list.d/opensearch.list
apt update
apt install -y opensearch
```

Configuration d'OpenSearch :

```bash
nano /etc/opensearch/opensearch.yml
```

Modifiez les paramètres suivants :

```yaml
cluster.name: graylog
node.name: node-1
bootstrap.memory_lock: true
network.host: 0.0.0.0
http.port: 9200
discovery.type: single-node
plugins.security.disabled: true
jvm.options: -Xms2g -Xmx4g
```

Activez le service :

```bash
systemctl enable opensearch
systemctl start opensearch
```

### 5. Installation de Graylog Server

```bash
apt install -y apt-transport-https curl gnupg
curl -fsSL https://packages.graylog2.org/repo/debian/pubkey.gpg | apt-key add -
echo "deb https://packages.graylog2.org/repo/debian/ bullseye 6.1" > /etc/apt/sources.list.d/graylog.list
apt update
apt install -y graylog-server
```

Configuration initiale :

```bash
nano /etc/graylog/server/server.conf
```

Générez les secrets nécessaires :

```bash
pwgen -N 1 -s 96
# Copier la valeur pour password_secret

echo -n "admin" | sha256sum
# Copier le hash pour root_password_sha2
```

Modifiez les paramètres :

```ini
password_secret = <valeur générée par pwgen>
root_password_sha2 = <valeur générée par sha256sum>
http_bind_address = 0.0.0.0:9000
elasticsearch_hosts = http://localhost:9200
```

Activez Graylog :

```bash
systemctl enable graylog-server
systemctl start graylog-server
```

---

## Centralisation des Logs Linux

### Configuration Graylog

#### Création de l'Input

1. Accédez à **System > Inputs**
2. Sélectionnez **Syslog UDP** dans le menu déroulant
3. Cliquez sur **Launch new input**
4. Configurez :
   - **Title** : `Linux_rsyslog_input`
   - **Port** : `12514`
   - **Store full message** : ✓
   - **Timezone** : `Europe/Paris`

#### Création de l'Index

1. Allez à **System > Indices > Create index set**
2. Nommez-le : `linux-index`
3. Sélectionnez un template par défaut
4. Validez

#### Création du Stream

1. Accédez à **Streams** et créez un nouveau stream
2. **Name** : `linux-stream`
3. **Index Set** : `linux-index`
4. Ajoutez une règle :
   - **Type** : `match input`
   - **Input** : `Linux_rsyslog_input`

### Configuration Linux (rsyslog)

#### Installation

```bash
apt install -y rsyslog
```

#### Configuration

Créez le fichier `/etc/rsyslog.d/1-Linux-graylog` :

```bash
cat > /etc/rsyslog.d/1-Linux-graylog << 'EOF'
*.* @172.16.0.6:12514;RSYSLOG_SyslogProtocol23Format
EOF
```

**Paramètres :**

| Paramètre | Signification |
|-----------|---------------|
| `*.*` | Tous les logs du système |
| `@` | Transport UDP (`@@` pour TCP) |
| `172.16.0.6:12514` | Serveur Graylog et port |
| `RSYSLOG_SyslogProtocol23Format` | Format RFC 3164 |

#### Redémarrage

```bash
systemctl restart rsyslog
```

### Vérification

Les logs Linux apparaissent dans Graylog dans le stream `linux-stream`.

---

## Centralisation des Logs Windows

### Configuration Graylog

#### Création de l'Input GELF UDP

1. Accédez à **System > Inputs**
2. Sélectionnez **GELF UDP** dans le menu déroulant
3. Configurez :
   - **Title** : `Windows_NXLog_input`
   - **Port** : `12201`

#### Création de l'Index

1. **System > Indices > Create index set**
2. **Name** : `windows-index`

#### Création du Stream

1. **Streams** > Nouveau stream
2. **Name** : `windows-stream`
3. **Index Set** : `windows-index`
4. Ajoutez une règle : **match input** = `Windows_NXLog_input`

### Installation de NXLog Community Edition

#### Téléchargement et Installation

```powershell
# Téléchargez depuis https://nxlog.co/products/nxlog-ce
# Installez le MSI
```

#### Configuration de NXLog

Modifiez `C:\Program Files\nxlog\conf\nxlog.conf` :

```ini
<Extension gelf>
    Module xm_gelf
</Extension>

<Input windows_eventlog>
    Module im_msvistalog
    SavePos TRUE
    Query <QueryList>\
        <Query Id="0">\
            <Select Path="System">*</Select>\
            <Select Path="Security">*</Select>\
            <Select Path="Application">*</Select>\
        </Query>\
    </QueryList>
</Input>

<Output graylog>
    Module om_udp
    Host 172.16.0.6
    Port 12201
    OutputType GELF
    Exec $Hostname = hostname();
</Output>

<Route windows_to_graylog>
    Path windows_eventlog => graylog
</Route>
```

**Explication des modules :**

| Module | Fonction |
|--------|----------|
| `xm_gelf` | Formatage GELF pour Graylog |
| `im_msvistalog` | Collecte Event Log Windows |
| `om_udp` | Envoi UDP vers Graylog |

#### Redémarrage du Service

```powershell
Restart-Service nxlog
```

### Filtrage par Event ID

Pour filtrer les événements d'authentification :

1. Modifiez la Query dans `nxlog.conf` :

```ini
<Query Id="0">
    <Select Path="Security">
        *[System[(EventID=4776 or EventID=4771)]]
    </Select>
</Query>
```

### Génération de Logs avec Kerbrute (Optionnel)

#### Installation de Kerbrute sur Kali Linux

```bash
cd /opt
wget https://github.com/ropnop/kerbrute/releases/download/v1.0.3/kerbrute_linux_amd64
chmod +x kerbrute_linux_amd64
ln -s kerbrute_linux_amd64 kerbrute
```

#### Attaque par Brute Force

```bash
./kerbrute bruteuser -d sodecaf.local --dc 172.16.0.1 \
    /usr/share/sqlmap/data/txt/wordlist.txt administrateur
```

#### Vérification dans Graylog

Filtrez avec :
- **EventID: 4776** → NTLM brute force
- **EventID: 4771** → Kerberos password spraying

---

## Centralisation des Logs Stormshield

### Configuration Graylog

#### Création de l'Input Syslog UDP

1. **System > Inputs** → **Syslog UDP**
2. **Title** : `Stormshield_input`
3. **Port** : `1514`

#### Création de l'Index et du Stream

1. Index : `stormshield-index`
2. Stream : `stormshield-stream` avec règle `match input = Stormshield_input`

### Configuration du Pare-feu Stormshield

1. **Configuration > Système > Configuration** → Ajoutez serveur NTP (ntp.univ-rennes2.fr)
2. **Configuration > Notifications > Traces – Syslog IPFIX > Syslog**
3. Configurez :
   - **Destination** : `172.16.0.6`
   - **Port** : `1514`
   - **Format** : Syslog

### Installation du Content Pack

Installez le content pack depuis GitHub :

```bash
# Téléchargez le JSON depuis :
# https://github.com/s0p4L1n3/Graylog_Content_Pack_Stormshield_Firewall

# Modifiez le nom du pare-feu dans le JSON
sed -i 's/firewall.lab.lan/VMSNSX09K0639A9/g' content-pack.json

# Importez dans Graylog via System > Content Packs
```

---

## Résumé des Ports et Services

| Service | Protocole | Port | Utilisation |
|---------|-----------|------|------------|
| Graylog Web UI | HTTP | 9000 | Accès à l'interface web |
| Linux rsyslog | UDP/TCP | 12514 | Réception des logs Linux |
| Windows NXLog | UDP | 12201 | Réception des logs Windows (GELF) |
| Stormshield | UDP | 1514 | Réception des logs Stormshield |

---

## Notes importantes

- **Adresse IP Graylog** : Les exemples utilisent `172.16.0.6`. Remplacez-la par l'IP de votre serveur.
- **Mots de passe** : Les exemples utilisent `Rootsio2017`. Utilisez des mots de passe robustes en production.
- **Fuseau horaire** : Les configurations utilisent `Europe/Paris`. Adaptez selon votre région.
