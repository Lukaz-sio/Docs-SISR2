# Guide Complet : Configuration et Utilisation de Graylog

Ce guide détaille la configuration de Graylog pour la centralisation des logs provenant de différentes sources : Linux, Windows et Stormshield.

---

## Table des matières

1. [Centralisation des logs Linux](#centralisation-des-logs-linux)
2. [Centralisation des logs Windows](#centralisation-des-logs-windows)
3. [Centralisation des logs Stormshield](#centralisation-des-logs-stormshield)
4. [Troubleshooting](#troubleshooting)

---

## Centralisation des logs Linux

### Étape 1 : Configuration de Graylog pour recevoir les logs

Avant de pouvoir recevoir des logs depuis un équipement Linux, vous devez mettre en place trois éléments essentiels :

- **Input** : Point d'entrée pour la réception des logs
- **Index** : Stockage et indexation des données
- **Stream** : Routage des logs vers l'index approprié

#### Création de l'Input

1. Accédez au menu **System > Inputs**
2. Dans le menu déroulant, sélectionnez **Syslog UDP**
3. Cliquez sur **Launch new input**
4. Configurez les paramètres suivants :
   - **Title** : `Graylog_UDP_rsyslog_input`
   - **Port** : `12514`
   - **Store full message** : Cochez cette option
   - **Time Zone** : Sélectionnez `UTC+01:00-Europe/Paris`
   - Conservez les autres paramètres par défaut

#### Création de l'Index

1. Accédez à **System > Indices > Create index set**
2. Nommez l'index : `linux-index`
3. Sélectionnez un template par défaut
4. Validez

#### Création du Stream

1. Accédez à **Streams** et créez un nouveau stream
2. Configurez les paramètres :
   - **Name** : `linux-stream`
   - **Index Set** : Sélectionnez `linux-index`
   - **Remove matches from 'Default Stream'** : Cochez cette option
3. Cliquez sur **more** pour ajouter les règles
4. Accédez à **manage Rules** > **add stream Rule**
   - **Type** : `match input`
   - **Input** : Sélectionnez `Graylog_UDP_rsyslog_input`
5. Validez

### Étape 2 : Configuration du serveur Linux

#### Installation de rsyslog

Connectez-vous au serveur Linux et installez rsyslog :

```bash
apt install rsyslog
```

#### Configuration de rsyslog

Créez un fichier de configuration dans le répertoire rsyslog.d :

```bash
nano /etc/rsyslog.d/1-Linux-graylog
```

Insérez la ligne suivante :

```ini
*.* @172.16.0.6:12514;RSYSLOG_SyslogProtocol23Format
```

**Explication des paramètres :**

| Paramètre | Signification |
|-----------|---------------|
| `*.*` | Envoie tous les logs Syslog de la machine Linux vers Graylog |
| `@` | Transport en UDP (utilisez `@@` pour TCP) |
| `172.16.0.6:12514` | Adresse IP du serveur Graylog et port d'écoute |
| `RSYSLOG_SyslogProtocol23Format` | Format des messages Syslog |

#### Redémarrage du service

Sauvegardez les modifications et redémarrez rsyslog :

```bash
systemctl restart rsyslog
```

Les premiers logs devraient apparaître dans votre Graylog !

---

## Centralisation des logs Windows

### Étape 1 : Configuration de Graylog pour recevoir les logs Windows

#### Création de l'Input

1. Accédez à **System > Inputs**
2. Sélectionnez le protocole **GELF UDP**
3. Nommez-le : `Win_Log_TVC`
4. Validez

#### Création de l'Index

1. Accédez à **System > Indices**
2. Créez un nouvel index set
3. Nommez-le : `index_win_log`
4. Ajoutez une description appropriée
5. Validez

#### Création du Stream

1. Accédez à **Streams** et créez un nouveau stream
2. Configurez les paramètres :
   - **Name** : `stream_win_log`
   - **Index Set** : `index_win_log`
   - **Remove matches from 'default stream'** : Cochez cette option
3. Accédez à **manage Rules** > **add stream Rule**
   - **Type** : `match input`
   - **Input** : Sélectionnez `win_log_tvc`
4. Validez

### Étape 2 : Installation et configuration de NXLog

NXLog est un agent permettant de capturer les journaux Windows et de les envoyer à Graylog, car Windows n'a pas cette capacité nativement.

#### Installation de NXLog

1. Téléchargez NXLog Community Edition (fichier `nxlog-ce-3.2.2329.msi`)
2. Consultez le tutoriel : https://www.it-connect.fr/envoyer-les-logs-windows-vers-graylog-avec-nxlog/
3. Installez NXLog sur le serveur Windows (ex: SRV-WIN1)

#### Configuration de NXLog

1. Ouvrez une console PowerShell ISE en tant qu'administrateur
2. Modifiez le fichier de configuration : `C:\Program Files\nxlog\conf\nxlog.conf`
3. Ajoutez les lignes suivantes à la fin du fichier :

```ini
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

# Déclarer le serveur Graylog
<Extension gelf>
Module xm_gelf
</Extension>

<Output graylog_udp>
Module om_udp
Host 172.16.0.6
Port 12201
OutputType GELF_UDP
</Output>

# Routage des flux
<Route 1>
Path in => graylog_udp
</Route>
```

#### Explication de la configuration NXLog

| Module / Bloc | Description |
|---------------|-------------|
| `im_msvistalog` | Module d'entrée pour récupérer les journaux depuis l'Observateur d'événements. Compatible Windows Server 2008 et supérieur (Windows Vista, Windows 11, Windows Server 2025, etc.). Pour versions antérieures, utilisez `im_mseventlog`. |
| `om_udp` | Module de sortie UDP. Modifiez l'adresse IP (172.16.0.6) si votre serveur Graylog a une IP différente. |
| `OutputType GELF_UDP` | Format de sortie conforme à l'Input Graylog créé. |
| `<Route 1>` | Règle de routage pour diriger les logs de l'entrée "in" vers la sortie "graylog_udp". |
| `<Select Path='Security'>*</Select>` | Filtre pour envoyer uniquement les événements du journal "Sécurité". Modifiez le chemin pour d'autres journaux. |

#### Redémarrage du service NXLog

Sauvegardez les modifications et redémarrez le service NXLog :

```powershell
Restart-Service nxlog
```

Vous pouvez également redémarrer via la console Services de Windows.

#### Vérification et dépannage

Si la configuration ne fonctionne pas, consultez le fichier de logs de NXLog :

```
C:\Program Files\nxlog\data\nxlog.log
```

### Étape 3 : Réception des logs dans Graylog

1. Accédez à **Search** dans Graylog
2. Vous devriez voir les premiers journaux arriver
3. Utilisez le bouton de rafraîchissement automatique (par défaut : 5 secondes)
4. Cliquez sur un log pour visualiser son contenu détaillé

#### Exemple de filtrage

Pour identifier les tentatives de connexion infructueuses, filtrez par Event ID :

```
EventID : 4776
```
ou
```
EventID : 4771
```

Ces Event IDs correspondent respectivement à :
- **4776** : NTLM bruteforce
- **4771** : Password spraying bruteforce

Pour générer ces événements, ajustez la stratégie d'audit Windows via une GPO.

---

## Centralisation des logs Stormshield

### Étape 1 : Configuration du pare-feu Stormshield

#### Configuration du serveur NTP

1. Accédez à **Configuration > Système > Configuration**
2. Ajoutez le serveur NTP de l'université de Rennes 2 : `ntp.univ-rennes2.fr`

#### Configuration de l'envoi des logs

1. Accédez à **Configuration > Notifications > Traces – Syslog IPFIX > Syslog**
2. Configurez Stormshield pour envoyer les logs au format Syslog
3. Cible : Serveur Graylog
4. Port UDP personnalisé : `1514`

### Étape 2 : Configuration de Graylog pour Stormshield

#### Création de l'Input

1. Accédez à **System > Inputs**
2. Sélectionnez le protocole **Syslog UDP**
3. Nommez-le : `Stormshield_UDP`
4. **Port** : `1514`
5. Validez

#### Création de l'Index

1. Accédez à **System > Indices > Create index set**
2. Nommez-le : `Index_Stormshield`
3. Sélectionnez un template par défaut
4. Validez

#### Création du Stream

1. Accédez à **Streams** et créez un nouveau stream
2. Configurez les paramètres :
   - **Name** : `Stormshield`
   - **Index Set** : `Index_Stormshield`
3. Accédez à **manage Rules** > **add stream Rule**
   - **Type** : `match input`
   - **Input** : Sélectionnez `Stormshield_UDP`
4. Validez

### Étape 3 : Installation d'un Content Pack Stormshield

Les Content Packs permettent d'importer, parser et créer des dashboards automatiquement.

#### Téléchargement et modification

1. Accédez au repository : https://github.com/s0p4L1n3/Graylog_Content_Pack_Stormshield_Firewall
2. Téléchargez le fichier JSON
3. Modifiez le nom du pare-feu : Remplacez `firewall.lab.lan` par votre hostname Stormshield (ex: `VMSNSX09K0639A9`)

#### Installation du Content Pack

1. Dans Graylog, accédez à **System > Content Packs**
2. Importez le fichier JSON modifié
3. Installez le Content Pack

Un nouvel Input, Stream et Dashboard seront créés automatiquement.

#### Exploitation des logs

1. Accédez au Dashboard Stormshield créé
2. Analysez les logs pour identifier les attaques et tentatives non autorisées
3. Modifiez le Dashboard si nécessaire pour adapter les visualisations

---

## Troubleshooting

### Problème : Serveur NTP bloqué sur Stormshield

**Symptôme** : Le serveur NTP de Rennes est bloqué avec le message "NTP : possible attaque de type poisoning"

**Solution** :

1. Accédez à **Monitoring > Tous les journaux**
2. Recherchez la ligne de log correspondante au bloc du serveur NTP
3. Clic droit > **Accéder à la configuration des alarmes**
4. Recherchez "NTP : possible attaque de type poisoning"
5. Cochez l'option pour **Autoriser ce message**

### Problème : Warning lors de l'import de logs

**Symptôme** : Message `libnsock ssl_init_helper(): OpenSSL legacy provider failed to load`

**Solution** : Ce warning peut être ignoré sans impact sur le fonctionnement.

### Problème : NXLog ne fonctionne pas

**Solution** :

1. Vérifiez le fichier de logs de NXLog : `C:\Program Files\nxlog\data\nxlog.log`
2. Vérifiez la syntaxe du fichier `nxlog.conf`
3. Vérifiez que l'adresse IP et le port Graylog sont corrects
4. Assurez-vous que le service NXLog est en cours d'exécution

---

## Résumé des ports utilisés

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
