# Centralisation et Analyse des Logs de l'Infrastructure SODECAF avec Graylog

## 📝 Introduction & Objectif

Ce Travail Pratique (TP) vise à mettre en place une solution complète de **centralisation, d'analyse et d'alerte des journaux (logs)** sur le serveur **Graylog** pour l'infrastructure SODECAF. [cite_start]La centralisation des logs est un élément fondamental de la sécurité et de la traçabilité des événements dans un Système d'Information (SI)[cite: 2360, 2377].

**Objectifs du TP :**
1.  **Installer et préparer** le serveur Graylog (SRV-GRAYLOG).
2.  **Centraliser les logs** des systèmes Windows (SRV-WIN1), Linux (SRV-WEB1) et des équipements réseau (Switch Cisco, Stormshield).
3.  **Analyser et visualiser** les données via l'utilisation d'Extractors et la création d'un **Dashboard**.
4.  Mettre en place des **alertes par e-mail** via Gmail pour les événements critiques (ex: échecs de connexion SSH).


---

## ⚙️ Prérequis (Matériel, Logiciel, Connaissances)

### Infrastructure SODECAF
| Hôte | OS / Rôle | IP | Remarques |
| :--- | :--- | :--- | :--- |
| **SRV-GRAYLOG** | Debian 12 / Graylog Server | `172.16.0.6` | 8 Go de RAM, 20 Go de disque. |
| **SRV-WIN1** | Windows Server / AD, DHCP, DNS | `172.16.0.1` | Agent NXLog. |
| **SRV-WEB1** | Debian 12 / Serveur Web (DMZ) | `192.168.0.1` | Rsyslog. |
| **Stormshield** | Routeur pare-feu | LAN : `172.16.0.254` | Envoi Syslog (UDP 1514). |
| **Commutateur Cisco** | Switch 2960 | `172.16.0.252` | Envoi Syslog (UDP 514). |

### Logiciels
* **NXLog Community Edition** (`nxlog-ce-3.2.2329.msi`) pour Windows.
* **Kerbrute** pour Kali Linux.
* Client mail `s-nail` pour les tests SMTP.

---

## 🛠️ Étapes Détaillées de Mise en Œuvre

### Étape 1: Installation et Configuration de Graylog (SRV-GRAYLOG)

1.  **Préparation de la VM :**
    * [cite_start]Importez la VM Debian 12 avec 8 Go de RAM et 20 Go de disque dur[cite: 2385].
    * Configurez l'adresse IP statique : `172.16.0.6`.

2.  **Synchronisation de l'Horloge (NTP) :**
    * [cite_start]La synchronisation de l'heure est essentielle pour l'analyse des logs[cite: 2413].
    * Appliquez le fuseau horaire Europe/Paris :
    ```bash
    timedatectl set-timezone Europe/Paris
    ```
    * Éditez le fichier `/etc/systemd/timesyncd.conf` :
    ```conf
    [Time]
    NTP=ntp.univ-rennes2.fr
    FallbackNTP=0.debian.pool.ntp.org 1.debian.pool.ntp.org 2.debian.pool.ntp.org 3.debian.pool.ntp.org
    ```
    * [cite_start]Activez le service NTP et vérifiez le statut (le port UDP 123 doit être ouvert sur le pare-feu si nécessaire)[cite: 2450].
    ```bash
    timedatectl set-ntp true
    systemctl restart systemd-timesyncd
    ```

3.  **Installation de Graylog :**
    * [cite_start]Suivez le tutoriel d'installation de Graylog (MongoDB et Elasticsearch/Opensearch non inclus ici, le TP supposant l'installation de base réussie)[cite: 2389, 2391].
    * Accédez à l'interface web : `http://172.16.0.6:9000`.
    * [cite_start]Connexion par défaut : `admin` / (mot de passe entré lors de l'installation)[cite: 2394].

---

### Étape 2: Centralisation des Logs Windows (SRV-WIN1)

#### 2.1. Configuration de Graylog (Input GELF UDP)
1.  **Créez l'Input pour Windows Logs :**
    * **Menu :** `System` > `Inputs`.
    * Sélectionnez `GELF UDP` et cliquez sur `Launch new input`.

| Paramètre | Valeur |
| :--- | :--- |
| **Title** | `win_log_tvc` (Exemple) |
| **Bind address** | `0.0.0.0` |
| **Port** | `12201` |
| **Node** | `srv-graylog` |

2.  **Créez l'Index et le Stream :**
    * [cite_start]**Index Set :** `index_win_log` (Max. in storage: 40 days, Min. in storage: 30 days)[cite: 55, 61].
    * **Stream :** `Stream win log`.
    * [cite_start]**Index Set associé :** `index_win_log`[cite: 75, 77].
    * **Règle de Stream :** Liez le Stream à l'Input.
    ```
    gl_source_input must match input win_log_tvc (GELF UDP: ...)
    ```

#### 2.2. Configuration de l'Agent NXLog (SRV-WIN1)
1.  **Installation de NXLog :**
    * [cite_start]Installez l'agent **NXLog Community** sur SRV-WIN1[cite: 91].
2.  **Configuration de nxlog.conf :**
    * Ouvrez `C:\Program Files\nxlog\conf\nxlog.conf` et ajoutez les blocs de configuration suivants (à la fin du programme) pour envoyer les événements de **Sécurité** vers Graylog :

    ```conf
# Récupérer les journaux de l'observateur d'événements
<Input in>
    Module          im_msvistalog
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
    Module          xm_gelf
</Extension>

<Output graylog_udp>
    Module          om_udp
    [cite_start]Host            172.16.0.6  # IP de SRV-GRAYLOG [cite: 183]
    Port            12201       # Port de l'Input GELF UDP
    OutputType      GELF_UDP
</Output>

# Routage des flux in vers out
<Route 1>
    Path            in => graylog_udp
</Route>
    ```

3.  **Redémarrage du service :**
    * Redémarrez le service NXLog via PowerShell (en Administrateur) :
    ```powershell
    Restart-Service nxlog
    ```

#### 2.3. Test et Recherche d'Authentification
1.  [cite_start]**Vérification :** Allez dans `Search` sur Graylog pour voir l'arrivée des logs Windows (pic de logs)[cite: 194, 195].
2.  **Configuration d'Audit AD (GPO) :**
    * Créez une GPO nommée `audit` sur le **Domain Controller** pour forcer l'enregistrement des événements de connexion.
    * **Chemin :** `Configuration ordinateur` > `Stratégies` > `Paramètres Windows` > `Paramètres de sécurité` > `Configuration avancée de l'audit` > `Connexion de compte`.
    * [cite_start]**Stratégies :** Réglez toutes les stratégies d'audit de validation des informations d'identification, Kerberos, et autres ouvertures de session sur **Succès, échec**[cite: 285, 286, 287, 288].
    * Forcez l'application de la GPO :
    ```cmd
    gpupdate /force
    ```

3.  **Génération de Logs d'Échec (Kerbrute) :**
    * Démarrez une VM **Kali Linux** dans le LAN.
    * [cite_start]Téléchargez et préparez Kerbrute[cite: 341, 342].
    * [cite_start]Lancez une attaque `bruteuser` pour générer des échecs d'authentification (EventID 4771 ou 4776)[cite: 295, 346, 352].

    ```bash
    # Télécharger et renommer kerbrute
    # (Supposons que kerbrute est dans le PATH et exécutable)

    # Commande pour bruteforce un utilisateur avec une wordlist (génère des échecs)
    kerbrute bruteuser -d sodecaf.local -dc 172.16.0.1 /usr/share/sqlmap/data/txt/wordlist.txt administrateur
    ```
4.  **Recherche dans Graylog :**
    * [cite_start]Observez l'arrivée des logs d'échec d'authentification[cite: 347].
    * [cite_start]Utilisez le filtre de recherche pour identifier les tentatives infructueuses (EventID 4776 ou 4771)[cite: 240, 352].
    ```
    EventID:4776 OR EventID:4771
    ```

---

### Étape 3: Centralisation des Logs Linux (SRV-WEB1)

#### 3.1. Configuration de Graylog (Input Syslog UDP)
1.  **Créez l'Input pour Linux Logs :**
    * **Menu :** `System` > `Inputs`.
    * [cite_start]Sélectionnez `Syslog UDP` et cliquez sur `Launch new input`[cite: 1116, 1123].

| Paramètre | Valeur |
| :--- | :--- |
| **Title** | `Graylog_udp_rsyslog_lamptvc` |
| **Bind address** | `0.0.0.0` |
| **Port** | `12514` |
| **Store full message?** | `✓` (Coché) |
| **Time Zone** | `UTC+02:00 - Europe/Paris` |

2.  **Créez l'Index et le Stream :**
    * **Index Set :** `lamptvc index`.
    * **Stream :** `lamptvc Stream` (Description : `log site web`).
    * [cite_start]**Règle de Stream :** Liez le Stream à l'Input `Graylog_udp_rsyslog_lamptvc` (Type : `match input`)[cite: 1177].

#### 3.2. Configuration de l'Agent Rsyslog (SRV-WEB1)
1.  **Installation de Rsyslog :**
    * Sur SRV-WEB1 (Debian 12), mettez à jour les paquets et installez Rsyslog :
    ```bash
    apt update
    apt install rsyslog
    systemctl status rsyslog
    ```

2.  **Configuration du Transfert :**
    * Créez le fichier de configuration dans le répertoire de Rsyslog :
    ```bash
    nano /etc/rsyslog.d/1-Linux-graylog.conf
    ```
    * Insérez la ligne pour envoyer tous les logs (`*.*`) vers Graylog en UDP (`@`) :
    ```conf
    *.* @172.16.0.6:12514;RSYSLOG_SyslogProtocol23Format
    ```
3.  **Redémarrage du service :**
    ```bash
    systemctl restart rsyslog
    ```

#### 3.3. Test et Recherche d'Échecs SSH
1.  **Génération d'échecs :**
    * [cite_start]Depuis une machine distante, tentez une connexion SSH à SRV-WEB1 avec un nom d'utilisateur et un mot de passe incorrects[cite: 1221, 1222].
    * [cite_start]Ceci génère des messages dans `/var/log/auth.log`[cite: 1223].
2.  **Recherche dans Graylog :**
    * Filtrez les échecs de connexion SSH :
    ```
    message:Failed password AND application_name:sshd
    ```
    * Pour un hôte spécifique :
    ```
    message:Failed password AND application_name:sshd AND source:srv-web1
    ```

---

### Étape 4: Centralisation des Logs Cisco (Switch 2960)

#### 4.1. Configuration de Graylog (Input Syslog UDP 514)
1.  **Créez l'Input pour Cisco Logs :**
    * **Menu :** `System` > `Inputs`.
    * [cite_start]Sélectionnez `Syslog UDP` et cliquez sur `Launch new input`[cite: 379].
    * Port : `514` (Port Syslog standard).
    * [cite_start]**Title** : `Switch Cisco` (Exemple)[cite: 402].

2.  **Créez l'Index et le Stream :**
    * **Index Set :** `switch index`.
    * [cite_start]**Rotation & Retention :** Max days: 40, Min days: 30[cite: 465, 468].
    * **Stream :** `switch stream`.
    * [cite_start]**Règle de Stream :** Liez le Stream à l'Input `Switch Cisco` (Type : `match input`)[cite: 482].

#### 4.2. Configuration du Switch Cisco
1.  **Configuration de l'Heure (NTP si possible) :**
    * Vérifiez l'heure : `SWITCH#show clock detail`
    * Synchronisation manuelle :
    ```cisco
    SWITCH#clock set 15:25:00 july 23 2022
    ```
    * Configuration NTP (si Internet disponible) :
    ```cisco
    SWITCH#conf t
    SWITCH(config)#ntp server 0.fr.pool.ntp.org
    SWITCH(config)#end
    ```

2.  **Configuration de l'Envoi des Logs :**
    * [cite_start]L'IP du serveur Graylog est `172.16.0.6`[cite: 527].
    * **Attention :** Le port de la commande ci-dessous (`5148`) ne correspond pas au port `514` de l'Input Graylog. Utilisez `514` si l'Input Graylog est sur ce port.

    ```cisco
    SWITCH#conf t
    SWITCH(config)#service timestamps log datetime
    SWITCH(config)#logging origin-id string SWITCH-ETAGE2-BAIE1
    SWITCH(config)#logging trap notifications
    SWITCH(config)#logging host 172.16.0.6 transport udp port 514
    SWITCH(config)#end
    SWITCH#copy running-config startup-config
    ```

3.  [cite_start]**Test :** Branchez/débranchez un port du switch (`port up/port down`) et vérifiez les logs sur Graylog[cite: 531, 532].

#### 4.3. Attaque et Parade (Port-Security)
1.  **Attaque Mac Flooding :**
    * Depuis la Kali, lancez l'attaque (nécessite l'outil `macof`) :
    ```bash
    macof -i eth0
    ```
    * [cite_start]Observez le gonflement de la table d'adresses MAC du switch : `SWITCH#show mac address-table count`[cite: 553].
2.  **Parade (Port Security) :**
    * [cite_start]Activez `port-security` avec le mode `restrict` sur l'interface de la Kali pour générer des logs en cas d'attaque[cite: 553].

---

### Étape 5: Centralisation des Logs Stormshield

1.  **Configuration du Stormshield :**
    * **Menu :** `Configuration` > `Système` > `Configuration` (NTP).
    * **Menu :** `Configuration` > `Notifications` > `Traces - Syslog IPFIX` > `Syslog`.
    * [cite_start]Créez/modifiez un profil Syslog (ex: `Syslog Profile 0`)[cite: 2167, 2169].
    * **Serveur Syslog :** `SRV-GRAYLOG` (`172.16.0.6`).
    * **Protocole :** `UDP`.
    * [cite_start]**Port :** `syslogUDP_custom` (`1514`)[cite: 2159, 2182].
    * **Format :** `RFC5424`.

2.  **Configuration de Graylog (Input Syslog UDP 1514) :**
    * **Menu :** `System` > `Inputs`.
    * [cite_start]Créez une nouvelle Input `Stormshield_UDP` (Type `Syslog UDP`) sur le port `1514`[cite: 2188].

3.  **Création de l'Index et du Stream :**
    * **Index Set :** `Index_Stormshield`.
    * **Stream :** `Stormshield`.
    * [cite_start]**Règle de Stream :** Liez le Stream à l'Input `Stormshield_UDP`[cite: 2190].

4.  **Utilisation d'un Content Pack :**
    * [cite_start]Téléchargez le Content Pack Stormshield[cite: 2237].
    * [cite_start]Modifiez le fichier JSON pour remplacer le nom du pare-feu par le nom réel du Stormshield (ex: `VMSNSX09K0639A9`)[cite: 2238].
    * [cite_start]Importez et installez le Content Pack pour créer Input, Stream, Extractors et Dashboard dédiés[cite: 2239].
    * [cite_start]Vérifiez l'arrivée des logs dans le Stream `Stormshield` et analysez-les[cite: 2191].

---

### Étape 6: Parsing des Logs et Création d'un Dashboard Web

#### 6.1. Import et Parsing des Logs Web (Exemple)

1.  **Préparation de l'Input TCP (Exemple d'import) :**
    * [cite_start]Créez une Input `Raw/Plaintext TCP` sur le port `5555` pour l'import de fichiers de logs[cite: 1585, 1603].
    * [cite_start]Créez l'Index Set `cybersec-lab-logs` (prefix `srvweb-test`) et le Stream `web-test` associé[cite: 1612, 1621, 1629, 1634].
    * [cite_start]Liez le Stream `web-test` à l'Input `Graylog_TCP_test_Linux` (Type `match input`)[cite: 1644].

2.  **Import des Logs (PC Hôte) :**
    * [cite_start]Envoyez le fichier `logs.txt` vers Graylog via `ncat` (le fichier `script.bat` utilise le port `5555`)[cite: 1665, 1669, 1670].

    ```cmd
    @echo off
    set GRAYLOG_HOST=172.16.0.6
    set GRAYLOG_PORT=5555
    for /f "delims=" %%l in (logs.txt) do (
        echo %%l | ncat.exe %GRAYLOG_HOST% %GRAYLOG_PORT%
    )
    ```

3.  **Création des Extractors :**
    * **Menu :** `System` > `Inputs` > `Manage extractors` (sur l'Input TCP `5555`).
    * [cite_start]**Logs JSON :** Créez un Extractor de type **JSON** (Nom : `srv-web-json`)[cite: 1735, 1736].
    * **Logs Apache/Nginx :** Créez un Extractor de type **GROK pattern** (Nom : `srv-web-grok`).

    ```grok
    %{IPORHOST:clientip} %{USER:ident} %{USER:auth} \[%{HTTPDATE:timestamp}\] "%{WORD:method} %{URIPATHPARAM:path} HTTP/%{NUMBER:httpversion}" %{NUMBER:status} (?:%{NUMBER:bytes}|-) "(?:%{URI:referrer}|-)" "%{DATA:useragent}"
    ```
    * [cite_start]Relancez l'import de logs pour appliquer le parsing[cite: 1743].

#### 6.2. Création du Dashboard Web
1.  **Menu :** `Dashboards` > `Create new dashboard`.
2.  **Widgets (Tableaux de bord) :**

    * **1. Nombre de requêtes reçues (Courbe) :**
        * **Type :** `Aggregation`.
        * **Group By :** `Row` > `timestamp`.
        * **Metrics :** `Function` > `Count`.
        * **Visualization :** `Line Chart`.

    * **2. Requêtes reçues (Tableau de messages) :**
        * **Type :** `Message Preview`.
        * **Fields :** `timestamp`, `source`, `MESSAGE PREVIEW`.
        * **Sorting :** `timestamp` / `Descending`.

    * **3. Top IP sources (Histogramme) :**
        * **Type :** `Aggregation`.
        * **Group By :** `Row` > `clientip`.
        * **Limit :** `15`.
        * **Metrics :** `Function` > `Count`, `Field` > `clientip`.
        * **Visualization :** `Bar Chart`.

    * **4. Requêtes suspectes (Tableau filtré) :**
        * **Type :** `Message Preview`.
        * **Filtre de recherche :**
        ```
        path:("/wp-admin" OR ".env") OR status:403
        ```
        * **Fields :** `timestamp`, `clientip`, `path`, `status`.

    * **Enregistrez** le Dashboard.

---

### Étape 7: Configuration des Alertes par E-mail (Gmail)

1.  **Configuration du Mot de Passe d'Application (Gmail) :**
    * Activez la validation en deux étapes sur votre compte Google.
    * [cite_start]Créez un **mot de passe d'application** dédié à Graylog (Sécurité > Validation en deux étapes > Mots de passe d'application)[cite: 1382, 1410].

2.  **Test SMTP (SRV-GRAYLOG) :**
    * Installez le client mail léger `s-nail` sur SRV-GRAYLOG (si non déjà présent) :
    ```bash
    apt install s-nail
    ```
    * Créez le fichier de configuration `/root/.mailrc` :
    ```bash
    cat > /root/.mailrc <<EOF
    set mta=smtp://smtp.gmail.com:587
    set smtp-use-starttls
    set smtp-auth=login
    set smtp-auth-user="votre_mail@gmail.com"
    set smtp-auth-password="mot_de_passe_de_l'application"
    set from="votre_mail@gmail.com"
    EOF
    ```
    * Testez l'envoi de mail :
    ```bash
    echo "Test d'envoi depuis le serveur Graylog" | s-nail -s "Test SMTP" votre_mail@gmail.com
    ```
    * [cite_start]**Vérification pare-feu :** Si `telnet smtp.gmail.com 587` échoue, vérifiez que le port TCP 587 est ouvert depuis le côté WAN du Stormshield[cite: 1422, 1423].

3.  **Mise en place de l'Alerte (Échecs SSH sur SRV-WEB1) :**
    * [cite_start]**Préparation du NAT :** Mettez en place temporairement une règle NAT entrante sur le Stormshield pour accéder en SSH à SRV-WEB1 depuis le WAN (PC Hôte)[cite: 1439].
    * **Création d'un Événement (Event Definition) :**
        * Créez une alerte pour un certain nombre d'échecs de connexion SSH sur le Stream Linux.
        * Condition : Recherche sur le message `Failed password` pour la source `srv-web1`.
    * **Création d'une Notification :**
        * **Menu :** `Alerts` > `Notifications`.
        * Créez une notification de type **Email** qui utilise le serveur SMTP configuré.
    * [cite_start]**Test :** Tentez une connexion SSH erronée à SRV-WEB1 (depuis le PC Hôte) et vérifiez la réception de l'e-mail d'alerte[cite: 1487, 1488].

---

## 📚 Conclusion et Références

Ce TP a permis la mise en place d'une solution complète de **SIEM / Log Management** en utilisant **Graylog**. L'infrastructure SODECAF est maintenant sous surveillance centralisée, permettant l'analyse de sécurité (parsing, dashboards) et la notification rapide des événements critiques via le service SMTP de Gmail.

### Références
* Tutoriel NXLog/Windows : `https://www.it-connect.fr/envoyer-les-logs-windows-vers-graylog-avec-nxlog/`
* Content Pack Stormshield : `https://github.com/s0p4L1n3/Graylog_Content_Pack_Stormshield_Firewall/blob/main/README.md`
* Tutoriel Alertes Email : `https://www.it-connect.fr/notifications-graylog-comment-envoyer-des-alertes-par-e-mail/`
* Configuration NTP/Synchronisation : (Annexe 1)