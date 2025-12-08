# Déploiement d'un SIEM/XDR Wazuh et Intégration ITSM avec GLPI

## 📝 Introduction & Objectif

[cite_start]Ce Travail Pratique (TP) vise à mettre en œuvre une chaîne de cybersécurité complète pour l'entreprise SODECAF[cite: 845, 3056]. [cite_start]Il combine la plateforme **Wazuh (SIEM/XDR)** pour la détection et la réponse aux menaces [cite: 872, 873][cite_start], et l'outil **GLPI (ITSM)** pour l'automatisation de la gestion des incidents (ticketing)[cite: 3058, 3086].

* [cite_start]**Wazuh** collecte, analyse, et corrèle les données de journaux (logs) provenant de diverses sources (firewalls, serveurs, applications, etc.)[cite: 849, 873]. [cite_start]Il permet de détecter les incidents de sécurité[cite: 850].
* [cite_start]**GLPI** (Gestionnaire Libre de Parc Informatique) permet de gérer l'ensemble des services informatiques [cite: 3085, 3061][cite_start], notamment la gestion des incidents (ticketing)[cite: 3063].

**Objectifs du TP :**
1.  [cite_start]Installer l'architecture Wazuh (Manager, Indexer, Dashboard)[cite: 894].
2.  [cite_start]Déployer les Agents Wazuh sur les endpoints[cite: 896].
3.  [cite_start]Simuler des attaques (Brute Force SSH, Scan Web) et observer la détection et la réponse active (blocage) de Wazuh[cite: 1120, 1137].
4.  [cite_start]Configurer l'intégration entre Wazuh et GLPI via l'API pour générer automatiquement des tickets incidents[cite: 3146, 3147].
5.  [cite_start]Tester la gestion des incidents dans GLPI[cite: 3371].

---

## ⚙️ Prérequis (Matériel, Logiciel, Connaissances)

### Infrastructure SODECAF
| Hôte | OS / Rôle | IP (Exemple) | Rôle dans l'architecture |
| :--- | :--- | :--- | :--- |
| **SRV-WAZUH** | Ubuntu 22.04 Server / Wazuh Manager/Indexer/Dashboard | `172.16.0.7` | [cite_start]Cœur du SIEM[cite: 954, 889, 892, 893]. |
| **SRV-GLPI** | Debian / Serveur GLPI (ITSM) | `172.16.0.8` | [cite_start]Gestion des tickets incidents[cite: 3138, 3086]. |
| **SRV-WIN1** | Windows Server / AD, DNS, DHCP | `172.16.0.1` | [cite_start]Endpoint Windows[cite: 952]. |
| **SRV-WEB (DVWA)** | Debian / Serveur Web Vulnérable | `192.168.0.1` | [cite_start]Endpoint Web en DMZ[cite: 936, 964]. |
| **OPNsense** | Routeur pare-feu | `172.16.0.254` | [cite_start]Pare-feu / Endpoint (Agent)[cite: 945, 1054]. |
| **Kali Linux** | Kali Linux | DHCP (LAN) | [cite_start]Machine d'attaque[cite: 955]. |



---

## 🛠️ Partie I : Déploiement de l'Infrastructure et des Agents Wazuh

### Étape 1: Installation et Préparation du SRV-WEB (DVWA)

1.  [cite_start]**Importation et Réseau :** Importez la VM Debian et configurez son IP statique (`192.168.0.1/24` en DMZ)[cite: 967, 934].
2.  [cite_start]**Configuration NTP :** Synchronisez l'horloge sur `Europe/Paris` et le serveur NTP `ntp.univ-rennes2.fr`[cite: 968, 971, 972].
    ```bash
    [cite_start]timedatectl set-timezone Europe/Paris # si besoin [cite: 970]
    # Éditez le fichier /etc/systemd/timesyncd.conf
    # [cite_start][Time] [cite: 971]
    # [cite_start]NTP=ntp.univ-rennes2.fr [cite: 972]
    [cite_start]timedatectl set-ntp true [cite: 974]
    [cite_start]systemctl restart systemd-timesyncd.service [cite: 975]
    [cite_start]timedatectl timesync-status [cite: 976]
    ```
3.  **Installation de DVWA :**
    * [cite_start]Le script installe Apache2, MariaDB-server et PHP[cite: 984].
    ```bash
    [cite_start]apt install curl [cite: 982]
    [cite_start]bash -c "$(curl --fail --show-error-silent-location [https://raw.githubusercontent.com/lamCarron/DVWA-Script/main/Install-DVWA.sh](https://raw.githubusercontent.com/lamCarron/DVWA-Script/main/Install-DVWA.sh))" [cite: 983]
    # [cite_start]Appuyez sur ENTREE sans entrer de mot de passe lors du script[cite: 981, 985].
    ```
4.  **Finalisation DVWA :**
    * [cite_start]Accédez à `http://192.168.0.1/DVWA`[cite: 986].
    * [cite_start]Connectez-vous avec `Username: admin`, `Password: password`[cite: 990].
    * [cite_start]Créez la base de données à partir de la page web (`Setup/Reset DB`)[cite: 991, 993].

### Étape 2: Installation du Serveur WAZUH (SRV-WAZUH)

1.  [cite_start]**Importation et Réseau :** Importez la VM Ubuntu 22.04 Server (`4Go` de RAM)[cite: 1003].
2.  [cite_start]**Configuration IP (Netplan) :** Créez le fichier `/etc/netplan/99_config.yaml` pour configurer l'IP statique (`172.16.0.7`)[cite: 1004].
    ```yaml
    [cite_start]network: [cite: 1005]
      [cite_start]version: 2 [cite: 1006]
      [cite_start]renderer: networkd [cite: 1007]
      [cite_start]ethernets: [cite: 1008]
        [cite_start]eth0: [cite: 1009] # Adaptez le nom de l'interface
          [cite_start]addresses: [cite: 1010]
            - 172.16.0.7/24 # Adaptez l'IP si nécessaire
          [cite_start]routes: [cite: 1012]
            - [cite_start]to: default [cite: 1013]
              via: 172.16.0.254 # Gateway OPNsense
          [cite_start]nameservers: [cite: 1015]
            addresses: [172.16.0.1, 1.1.1.1] # SRV-WIN1 et DNS public
    ```
    * [cite_start]Appliquez la configuration : `netplan apply`[cite: 1021].
    * [cite_start]Synchronisez le serveur WAZUH sur le même serveur NTP que le serveur web[cite: 1022].
3.  **Installation de Wazuh (Manager, Indexer, Dashboard) :**
    ```bash
    [cite_start]curl -sO [https://packages.wazuh.com/4.12/wazuh-install.sh](https://packages.wazuh.com/4.12/wazuh-install.sh) && sudo bash ./wazuh-install.sh -a [cite: 1024]
    ```
    * [cite_start]**Notez le mot de passe ADMIN** affiché à la fin de l'installation[cite: 1032].
4.  [cite_start]**Accès Dashboard :** Accédez à `https://172.16.0.7/`[cite: 1035].
    * [cite_start]Login : `admin` / Password : (mot de passe noté)[cite: 1036, 1031].

### Étape 3: Déploiement des Agents Wazuh sur les Endpoints

**⚠️ Attention :** Wazuh utilise les ports **1514 et 1515** (pour l'enregistrement et la communication). [cite_start]Pensez à les ouvrir sur le pare-feu OPNsense[cite: 1052]. [cite_start]Le paquet `iptables` est requis pour l'agent Wazuh sur Linux (SRV-WEB)[cite: 1148].

1.  **SRV-WIN1 :**
    * [cite_start]Installez l'agent Wazuh sur SRV-WIN1[cite: 1049].
2.  **SRV-WEB :**
    * [cite_start]Installez l'agent Wazuh sur le serveur web[cite: 1051].
3.  **OPNsense :**
    * [cite_start]Installez le greffon **`os-wazuh-agent`**[cite: 1054].
    * [cite_start]Configurez l'adresse IP du serveur Wazuh : `Services` > `Agent Wazuh` > `Paramètres`[cite: 1055].
4.  [cite_start]**Vérification :** Contrôlez que les machines apparaissent sur le Dashboard de Wazuh[cite: 1056].

---

## 🛠️ Partie II : Détection et Réponse Active (XDR)

### Étape 4: Scan des Vulnérabilités (Vulnerability Detection)

1.  [cite_start]**Analyse :** Wazuh, via ses agents, scanne les vulnérabilités connues (CVE) sur les endpoints[cite: 1121, 1136].
2.  [cite_start]**Vérification :** Cliquez sur les vulnérabilités les plus élevées sur le Dashboard[cite: 1132].
3.  [cite_start]**Analyse :** Relevez les numéros de **CVE** (format CVE-AAAA-NNNNNN) [cite: 1133] [cite_start]et observez les atténuations (mitigations) proposées[cite: 1134].

### Étape 5: Test d'Attaque Brute Force SSH (Réponse Active : Blocage)

1.  [cite_start]**Installation de `iptables` (SRV-WEB) :** Le paquet est nécessaire pour la commande `firewall-drop`[cite: 1148].
2.  **Configuration de la Réponse Active (SRV-WAZUH) :**
    * Modifiez le fichier de configuration du manager `/var/ossec/etc/ossec.conf`.
    * [cite_start]Vérifiez la présence de la commande `firewall-drop`[cite: 1143, 1144].
    * [cite_start]Ajoutez le bloc `active-response` pour la règle SSH Brute Force (ID 5763)[cite: 1153].

    ```xml
[cite_start]<command> [cite: 1143]
  [cite_start]<name>firewall-drop</name> [cite: 1144]
  [cite_start]<executable>firewall-drop</executable> [cite: 1145]
  [cite_start]<timeout_allowed>yes</timeout_allowed> [cite: 1146]
[cite_start]</command> [cite: 1147]

[cite_start]<active-response> [cite: 1153]
  [cite_start]<command>firewall-drop</command> [cite: 1154]
  [cite_start]<location>local</location> [cite: 1155]
  [cite_start]<rules_id>5763</rules_id> [cite: 1156] # Règle SSHD brute force trying
  [cite_start]<timeout>180</timeout> [cite: 1157] # Bannissement de 180s
[cite_start]</active-response> [cite: 1160]
    ```
    * [cite_start]Redémarrez le manager : `systemctl restart wazuh-manager`[cite: 1161].

3.  **Attaque (Kali Linux) :**
    * [cite_start]Lancez l'attaque Brute Force SSH contre SRV-WEB[cite: 1163, 1164].
    ```bash
    [cite_start]hydra -t 4 -l etudiant -P /usr/share/wordlists/rockyou.txt.gz 192.168.0.1 ssh [cite: 1164]
    ```

4.  **Vérification (Wazuh Dashboard) :**
    * Filtrez sur `rule.id is 5763`. [cite_start]L'attaque doit être détectée (MITRE T1110 - Brute Force)[cite: 1165, 1177].
    * [cite_start]Retirez le filtre et observez l'événement **Active Response** : `Host Blocked by firewall-drop Active Response` (rule.id 651)[cite: 1185, 1191].
    * [cite_start]Vérifiez que le test de connectivité de la Kali vers SRV-WEB n'aboutit plus (blocage temporaire)[cite: 1195].

### Étape 6: Détection d'Attaques Web (Teler NIDS)

1.  [cite_start]**Installation de Teler (SRV-WEB) :** Teler est un IDS (Intrusion Detection System) qui analyse les logs HTTP[cite: 1232, 1233].
    ```bash
    [cite_start]wget [https://github.com/teler-sh/teler/releases/download/v2.0.0/teler_2.0.0_linux_amd64.tar.gz](https://github.com/teler-sh/teler/releases/download/v2.0.0/teler_2.0.0_linux_amd64.tar.gz) [cite: 1236]
    [cite_start]tar -xvzf teler_2.0.0_linux_amd64.tar.gz [cite: 1236]
    [cite_start]mkdir /var/log/teler [cite: 1250]
    # [cite_start]Créez le fichier teler.yaml (avec le format de log Apache et la sortie /var/log/teler/output.log) [cite: 1240, 1248]
    ```

2.  **Configuration Agent Wazuh pour Teler (SRV-WEB) :**
    * [cite_start]Ajoutez la configuration ci-dessous au fichier `/var/ossec/etc/ossec.conf` pour lire les logs JSON de Teler[cite: 1252].
    ```xml
[cite_start]<localfile> [cite: 1253]
  [cite_start]<log_format>syslog</log_format> [cite: 1254]
  [cite_start]<location>/var/log/teler/output.log</location> [cite: 1255]
[cite_start]</localfile> [cite: 1256]
    ```
    * [cite_start]Redémarrez l'agent Wazuh : `systemctl restart wazuh-agent`[cite: 1257, 1258].

3.  **Lancement de Teler (SRV-WEB) :**
    * [cite_start]Teler est en attente de log Apache[cite: 1261].
    ```bash
    tail -f /var/log/apache2/access.log | [cite_start]./teler -c teler.yaml [cite: 1260]
    ```

4.  **Configuration des Règles et Réponse Active (SRV-WAZUH) :**
    * [cite_start]Ajoutez la commande `firewall-drop` dans `/var/ossec/etc/ossec.conf` pour les règles 100012, 100013 et 100014 (blocage de 360s)[cite: 1268, 1275].
    * [cite_start]Ajoutez les règles personnalisées 100012 à 100014 (associées aux MITRE T1210, T1590, T1595) dans `/var/ossec/etc/rules/local_rules.xml`[cite: 1278, 1290, 1299, 1308].
    * [cite_start]Redémarrez le manager Wazuh : `systemctl restart wazuh-manager`[cite: 1313, 1314].

5.  **Attaque (Kali Linux) :**
    * [cite_start]Lancez le scan de vulnérabilité avec Nikto[cite: 1315, 1318].
    ```bash
    [cite_start]nikto -h [http://192.168.0.1/DVWA](http://192.168.0.1/DVWA) [cite: 1318]
    ```

6.  **Vérification (Wazuh Dashboard) :**
    * [cite_start]L'attaque doit être détectée par Teler, notifiée à Wazuh (ex: `teler detected Bad Crawler`, rule.id 100013) et bloquée par l'Active Response[cite: 1319, 1344].

---

## 🛠️ Partie III : Gestion ITSM des Incidents (GLPI)

### Étape 7: Installation de GLPI (SRV-GLPI)

1.  **Importation et Réseau :** Importez la VM Debian et configurez son IP statique (`172.16.0.8`).
2.  [cite_start]**Installation :** GLPI est considéré comme installé et opérationnel pour cette activité[cite: 3139].

### Étape 8: Activation et Préparation de l'API GLPI

1.  [cite_start]**Accès GLPI :** Connectez-vous à `http://172.16.0.8/`[cite: 3142].
    * [cite_start]Admin par défaut : `glpi` / `glpi`[cite: 3144, 3145].
2.  **Activation de l'API :**
    * [cite_start]**Menu :** `Configuration` > `Générale` > `API`[cite: 3155].
    * [cite_start]`Activer l'API Rest` : `Oui`[cite: 3161].
    * [cite_start]`Activer la connexion avec un jeton externe` : `Oui`[cite: 3167, 3168].
    * [cite_start]Sauvegardez[cite: 3169].
3.  **Création du Client de l'API (`wazuh_api`) :**
    * [cite_start]Ajoutez un client de l'API (`wazuh_api`)[cite: 3175].
    * [cite_start]Filtrez l'accès avec l'adresse IPv4 de SRV-WAZUH (`172.16.0.7`) dans **Début** et **Fin de plage d'adresse IPv4**[cite: 3183, 3187, 3186].
    * [cite_start]**Régénérez le Jeton d'application (app\_token)**[cite: 3191].
4.  **Création de l'Utilisateur d'API (`wazuh`) :**
    * [cite_start]**Menu :** `Administration` > `Utilisateurs` > `Ajouter un utilisateur`[cite: 3194].
    * [cite_start]Créez l'utilisateur : `wazuh`[cite: 3202].
    * [cite_start]Dans **Clefs d'accès distant**, régénérez un **Jeton d'API (user\_token)**[cite: 3197, 3206].
5.  [cite_start]**Enregistrement :** Enregistrez l'**app\_token** et l'**user\_token**[cite: 3210].

### Étape 9: Automatisation des Tickets via Script (Active Response)

1.  **Préparation du Script (SRV-WAZUH) :**
    * [cite_start]Créez le fichier de log : `/var/log/glpi_ticket.log`[cite: 3275, 3323].
    * [cite_start]Copiez le script `glpi_ticket.sh` (voir ci-dessous) dans `/var/ossec/active-response/bin/glpi_ticket.sh`[cite: 3324].
    * [cite_start]**Modifiez** dans le script les variables `GLPI_URL`, `APP_TOKEN`, `USER_TOKEN`[cite: 3273, 3274, 3325].
    * Changez les permissions du script :
    ```bash
    [cite_start]chown root:wazuh /var/ossec/active-response/bin/glpi_ticket.sh [cite: 3326]
    [cite_start]chmod 750 /var/ossec/active-response/bin/glpi_ticket.sh [cite: 3326]
    ```

2.  **Test Manuel du Script :**
    ```bash
    echo '{"parameters":{"alert":{"rule":{"id":"5710","description":"Tentative brute force SSH", "level":10},"agent":{"id":"001","name":"srv-web"},"data":{"srcip":"172.16.0.50"},"full_log":"sshd failed login"}}}' | [cite_start]/var/ossec/active-response/bin/glpi_ticket.sh [cite: 3329]
    ```
    * [cite_start]Un ticket doit être créé sur GLPI[cite: 3327].

3.  **Configuration de la Réponse Active GLPI (SRV-WAZUH) :**
    * [cite_start]Modifiez le fichier `/var/ossec/etc/ossec.conf` pour activer la commande `glpi_ticket` (qui exécute le script `glpi_ticket.sh`) et l'associer à la règle 5763 (SSH Brute Force)[cite: 3344, 3354].
    ```xml
[cite_start]<command> [cite: 3345]
  [cite_start]<name>glpi_ticket</name> [cite: 3346]
  [cite_start]<executable>glpi_ticket.sh</executable> [cite: 3347]
  [cite_start]<expect>none</expect> [cite: 3348]
  [cite_start]<timeout_allowed>yes</timeout_allowed> [cite: 3349]
[cite_start]</command> [cite: 3350]
[cite_start]<active-response> [cite: 3351]
  [cite_start]<command>glpi_ticket</command> [cite: 3352]
  [cite_start]<location>server</location> [cite: 3353]
  [cite_start]<rules_id>5763</rules_id> [cite: 3354]
  [cite_start]<timeout>60</timeout> [cite: 3355]
[cite_start]</active-response> [cite: 3356]
    ```
    * [cite_start]Redémarrez le manager Wazuh : `systemctl restart wazuh-manager`[cite: 3345].

4.  **Test Final :**
    * [cite_start]Effectuez une attaque Brute Force SSH (règle 5763) avec la Kali[cite: 3357].
    * [cite_start]Vérifiez que le ticket incident est créé automatiquement dans GLPI[cite: 3358].

### Étape 10: Gestion des Tickets Incidents (GLPI)

1.  [cite_start]Connectez-vous à GLPI avec le compte administrateur `glpi` pour vérifier les droits ou avec le compte `SOC-N1`[cite: 3372].
2.  [cite_start]Testez les actions de gestion des incidents sur les tickets générés (réponse, escalade, clôture)[cite: 3372].

---

## 📚 Conclusion et Références

[cite_start]Ce TP a permis de déployer une solution de sécurité de bout en bout, associant **Wazuh (SIEM/XDR)** à la traçabilité et l'organisation offertes par **GLPI (ITSM)**[cite: 3058]. [cite_start]L'automatisation de la création de tickets via l'API [cite: 3147] [cite_start]est essentielle pour accélérer la gestion des incidents de sécurité au sein du SOC[cite: 3066].

### Références
* [cite_start]Documentation Wazuh : `https://documentation.wazuh.com/current/quickstart.html` [cite: 1420]
* [cite_start]Tutoriels spécifiques Wazuh (Active Response, Teler, Suricata)[cite: 1142, 1215, 1231, 1367].
* [cite_start]Tutoriel Alertes GLPI : (Chapitre III)[cite: 2164].