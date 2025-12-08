# Déploiement d'un SIEM/XDR Wazuh et Intégration ITSM avec GLPI

## 📝 Introduction & Objectif

Ce Travail Pratique (TP) vise à mettre en œuvre une chaîne de cybersécurité complète pour l'entreprise SODECAF[cite: 845, 3056]. Il combine la plateforme **Wazuh (SIEM/XDR)** pour la détection et la réponse aux menaces [cite: 872, 873], et l'outil **GLPI (ITSM)** pour l'automatisation de la gestion des incidents (ticketing)[cite: 3058, 3086].

* **Wazuh** collecte, analyse, et corrèle les données de journaux (logs) provenant de diverses sources (firewalls, serveurs, applications, etc.)[cite: 849, 873]. Il permet de détecter les incidents de sécurité[cite: 850].
* **GLPI** (Gestionnaire Libre de Parc Informatique) permet de gérer l'ensemble des services informatiques [cite: 3085, 3061], notamment la gestion des incidents (ticketing)[cite: 3063].

**Objectifs du TP :**
1.  Installer l'architecture Wazuh (Manager, Indexer, Dashboard)[cite: 894].
2.  Déployer les Agents Wazuh sur les endpoints[cite: 896].
3.  Simuler des attaques (Brute Force SSH, Scan Web) et observer la détection et la réponse active (blocage) de Wazuh[cite: 1120, 1137].
4.  Configurer l'intégration entre Wazuh et GLPI via l'API pour générer automatiquement des tickets incidents[cite: 3146, 3147].
5.  Tester la gestion des incidents dans GLPI[cite: 3371].

---

## ⚙️ Prérequis (Matériel, Logiciel, Connaissances)

### Infrastructure SODECAF
| Hôte | OS / Rôle | IP (Exemple) | Rôle dans l'architecture |
| :--- | :--- | :--- | :--- |
| **SRV-WAZUH** | Ubuntu 22.04 Server / Wazuh Manager/Indexer/Dashboard | `172.16.0.7` | Cœur du SIEM[cite: 954, 889, 892, 893]. |
| **SRV-GLPI** | Debian / Serveur GLPI (ITSM) | `172.16.0.8` | Gestion des tickets incidents[cite: 3138, 3086]. |
| **SRV-WIN1** | Windows Server / AD, DNS, DHCP | `172.16.0.1` | Endpoint Windows[cite: 952]. |
| **SRV-WEB (DVWA)** | Debian / Serveur Web Vulnérable | `192.168.0.1` | Endpoint Web en DMZ[cite: 936, 964]. |
| **OPNsense** | Routeur pare-feu | `172.16.0.254` | Pare-feu / Endpoint (Agent)[cite: 945, 1054]. |
| **Kali Linux** | Kali Linux | DHCP (LAN) | Machine d'attaque[cite: 955]. |



---

## 🛠️ Partie I : Déploiement de l'Infrastructure et des Agents Wazuh

### Étape 1: Installation et Préparation du SRV-WEB (DVWA)

1.  **Importation et Réseau :** Importez la VM Debian et configurez son IP statique (`192.168.0.1/24` en DMZ).
2.  **Configuration NTP :** Synchronisez l'horloge sur `Europe/Paris` et le serveur NTP `ntp.univ-rennes2.fr`.
    ```bash
    timedatectl set-timezone Europe/Paris
    # Éditez le fichier /etc/systemd/timesyncd.conf
    # [Time]
    # NTP=ntp.univ-rennes2.fr
    timedatectl set-ntp true
    systemctl restart systemd-timesyncd.service
    timedatectl timesync-status
    ```
3.  **Installation de DVWA :**
    * Le script installe Apache2, MariaDB-server et PHP.
    ```bash
    apt install curl
    bash -c "$(curl --fail --show-error-silent-location https://raw.githubusercontent.com/lamCarron/DVWA-Script/main/Install-DVWA.sh)"
    # Appuyez sur ENTREE sans entrer de mot de passe lors du script.
    ```
4.  **Finalisation DVWA :**
    * Accédez à `http://192.168.0.1/DVWA`.
    * Connectez-vous avec `Username: admin`, `Password: password`.
    * Créez la base de données à partir de la page web (`Setup/Reset DB`).

### Étape 2: Installation du Serveur WAZUH (SRV-WAZUH)

1.  **Importation et Réseau :** Importez la VM Ubuntu 22.04 Server (`4Go` de RAM).
2.  **Configuration IP (Netplan) :** Créez le fichier `/etc/netplan/99_config.yaml` pour configurer l'IP statique (`172.16.0.7`).
    ```yaml
    network:
      version: 2
      renderer: networkd
      ethernets:
        eth0: # Adaptez le nom de l'interface
          addresses: 
            - 172.16.0.7/24 # Adaptez l'IP si nécessaire
          routes: 
            - to: default 
              via: 172.16.0.254 # Gateway OPNsense
          nameservers: 
            addresses: [172.16.0.1, 1.1.1.1] # SRV-WIN1 et DNS public
    ```
    * Appliquez la configuration : `netplan apply`.
    * Synchronisez le serveur WAZUH sur le même serveur NTP que le serveur web.
3.  **Installation de Wazuh (Manager, Indexer, Dashboard) :**
    ```bash
    curl -sO https://packages.wazuh.com/4.12/wazuh-install.sh && sudo bash ./wazuh-install.sh -a
    ```
    * **Notez le mot de passe ADMIN** affiché à la fin de l'installation[cite: 1032].
4.  **Accès Dashboard :** Accédez à `https://172.16.0.7/`[cite: 1035].
    * Login : `admin` / Password : (mot de passe noté)[cite: 1036, 1031].

### Étape 3: Déploiement des Agents Wazuh sur les Endpoints

**⚠️ Attention :** Wazuh utilise les ports **1514 et 1515** (pour l'enregistrement et la communication). Pensez à les ouvrir sur le pare-feu OPNsense[cite: 1052]. Le paquet `iptables` est requis pour l'agent Wazuh sur Linux (SRV-WEB)[cite: 1148].

1.  **SRV-WIN1 :**
    * Installez l'agent Wazuh sur SRV-WIN1[cite: 1049].
2.  **SRV-WEB :**
    * Installez l'agent Wazuh sur le serveur web[cite: 1051].
3.  **OPNsense :**
    * Installez le greffon **`os-wazuh-agent`**[cite: 1054].
    * Configurez l'adresse IP du serveur Wazuh : `Services` > `Agent Wazuh` > `Paramètres`[cite: 1055].
4.  **Vérification :** Contrôlez que les machines apparaissent sur le Dashboard de Wazuh[cite: 1056].

---

## 🛠️ Partie II : Détection et Réponse Active (XDR)

### Étape 4: Scan des Vulnérabilités (Vulnerability Detection)

1.  **Analyse :** Wazuh, via ses agents, scanne les vulnérabilités connues (CVE) sur les endpoints[cite: 1121, 1136].
2.  **Vérification :** Cliquez sur les vulnérabilités les plus élevées sur le Dashboard[cite: 1132].
3.  **Analyse :** Relevez les numéros de **CVE** (format CVE-AAAA-NNNNNN) [cite: 1133] et observez les atténuations (mitigations) proposées[cite: 1134].

### Étape 5: Test d'Attaque Brute Force SSH (Réponse Active : Blocage)

1.  **Installation de `iptables` (SRV-WEB) :** Le paquet est nécessaire pour la commande `firewall-drop`[cite: 1148].
2.  **Configuration de la Réponse Active (SRV-WAZUH) :**
    * Modifiez le fichier de configuration du manager `/var/ossec/etc/ossec.conf`.
    * Vérifiez la présence de la commande `firewall-drop`[cite: 1143, 1144].
    * Ajoutez le bloc `active-response` pour la règle SSH Brute Force (ID 5763)[cite: 1153].

    ```xml
<command>
  <name>firewall-drop</name>
  <executable>firewall-drop</executable>
  <timeout_allowed>yes</timeout_allowed>
</command>

<active-response>
  <command>firewall-drop</command>
  <location>local</location>
  <rules_id>5763</rules_id>  # Règle SSHD brute force trying
  <timeout>180</timeout>  # Bannissement de 180s
</active-response>
    ```
    * Redémarrez le manager : `systemctl restart wazuh-manager`.

3.  **Attaque (Kali Linux) :**
    * Lancez l'attaque Brute Force SSH contre SRV-WEB[cite: 1163, 1164].
    ```bash
    hydra -t 4 -l etudiant -P /usr/share/wordlists/rockyou.txt.gz 192.168.0.1 ssh
    ```

4.  **Vérification (Wazuh Dashboard) :**
    * Filtrez sur `rule.id is 5763`. L'attaque doit être détectée (MITRE T1110 - Brute Force)[cite: 1165, 1177].
    * Retirez le filtre et observez l'événement **Active Response** : `Host Blocked by firewall-drop Active Response` (rule.id 651)[cite: 1185, 1191].
    * Vérifiez que le test de connectivité de la Kali vers SRV-WEB n'aboutit plus (blocage temporaire)[cite: 1195].

### Étape 6: Détection d'Attaques Web (Teler NIDS)

1.  **Installation de Teler (SRV-WEB) :** Teler est un IDS (Intrusion Detection System) qui analyse les logs HTTP[cite: 1232, 1233].
    ```bash
    wget https://github.com/teler-sh/teler/releases/download/v2.0.0/teler_2.0.0_linux_amd64.tar.gz
    tar -xvzf teler_2.0.0_linux_amd64.tar.gz
    mkdir /var/log/teler
    # Créez le fichier teler.yaml (avec le format de log Apache et la sortie /var/log/teler/output.log) [cite: 1240, 1248]
    ```

2.  **Configuration Agent Wazuh pour Teler (SRV-WEB) :**
    * Ajoutez la configuration ci-dessous au fichier `/var/ossec/etc/ossec.conf` pour lire les logs JSON de Teler[cite: 1252].
    ```xml
<localfile>
  <log_format>syslog</log_format>
  <location>/var/log/teler/output.log</location>
</localfile>
    ```
    * Redémarrez l'agent Wazuh : `systemctl restart wazuh-agent`.

3.  **Lancement de Teler (SRV-WEB) :**
    * Teler est en attente de log Apache.
    ```bash
    tail -f /var/log/apache2/access.log | ./teler -c teler.yaml
    ```

4.  **Configuration des Règles et Réponse Active (SRV-WAZUH) :**
    * Ajoutez la commande `firewall-drop` dans `/var/ossec/etc/ossec.conf` pour les règles 100012, 100013 et 100014 (blocage de 360s).
    * Ajoutez les règles personnalisées 100012 à 100014 (associées aux MITRE T1210, T1590, T1595) dans `/var/ossec/etc/rules/local_rules.xml`.
    * Redémarrez le manager Wazuh : `systemctl restart wazuh-manager`.

5.  **Attaque (Kali Linux) :**
    * Lancez le scan de vulnérabilité avec Nikto[cite: 1315, 1318].
    ```bash
    nikto -h http://192.168.0.1/DVWA
    ```

6.  **Vérification (Wazuh Dashboard) :**
    * L'attaque doit être détectée par Teler, notifiée à Wazuh (ex: `teler detected Bad Crawler`, rule.id 100013) et bloquée par l'Active Response[cite: 1319, 1344].

---

## 🛠️ Partie III : Gestion ITSM des Incidents (GLPI)

### Étape 7: Installation de GLPI (SRV-GLPI)

1.  **Importation et Réseau :** Importez la VM Debian et configurez son IP statique (`172.16.0.8`).
2.  **Installation :** GLPI est considéré comme installé et opérationnel pour cette activité[cite: 3139].

### Étape 8: Activation et Préparation de l'API GLPI

1.  **Accès GLPI :** Connectez-vous à `http://172.16.0.8/`[cite: 3142].
    * Admin par défaut : `glpi` / `glpi`[cite: 3144, 3145].
2.  **Activation de l'API :**
    * **Menu :** `Configuration` > `Générale` > `API`[cite: 3155].
    * `Activer l'API Rest` : `Oui`[cite: 3161].
    * `Activer la connexion avec un jeton externe` : `Oui`[cite: 3167, 3168].
    * Sauvegardez[cite: 3169].
3.  **Création du Client de l'API (`wazuh_api`) :**
    * Ajoutez un client de l'API (`wazuh_api`)[cite: 3175].
    * Filtrez l'accès avec l'adresse IPv4 de SRV-WAZUH (`172.16.0.7`) dans **Début** et **Fin de plage d'adresse IPv4**[cite: 3183, 3187, 3186].
    * **Régénérez le Jeton d'application (app\_token)**[cite: 3191].
4.  **Création de l'Utilisateur d'API (`wazuh`) :**
    * **Menu :** `Administration` > `Utilisateurs` > `Ajouter un utilisateur`[cite: 3194].
    * Créez l'utilisateur : `wazuh`[cite: 3202].
    * Dans **Clefs d'accès distant**, régénérez un **Jeton d'API (user\_token)**[cite: 3197, 3206].
5.  **Enregistrement :** Enregistrez l'**app\_token** et l'**user\_token**[cite: 3210].

### Étape 9: Automatisation des Tickets via Script (Active Response)

1.  **Préparation du Script (SRV-WAZUH) :**
    * Créez le fichier de log : `/var/log/glpi_ticket.log`.
    * Copiez le script `glpi_ticket.sh` (voir ci-dessous) dans `/var/ossec/active-response/bin/glpi_ticket.sh`.
    * **Modifiez** dans le script les variables `GLPI_URL`, `APP_TOKEN`, `USER_TOKEN`.
    * Changez les permissions du script :
    ```bash
    chown root:wazuh /var/ossec/active-response/bin/glpi_ticket.sh
    chmod 750 /var/ossec/active-response/bin/glpi_ticket.sh
    ```

2.  **Test Manuel du Script :**
    ```bash
    echo '{"parameters":{"alert":{"rule":{"id":"5710","description":"Tentative brute force SSH", "level":10},"agent":{"id":"001","name":"srv-web"},"data":{"srcip":"172.16.0.50"},"full_log":"sshd failed login"}}}' | /var/ossec/active-response/bin/glpi_ticket.sh
    ```
    * Un ticket doit être créé sur GLPI[cite: 3327].

3.  **Configuration de la Réponse Active GLPI (SRV-WAZUH) :**
    * Modifiez le fichier `/var/ossec/etc/ossec.conf` pour activer la commande `glpi_ticket` (qui exécute le script `glpi_ticket.sh`) et l'associer à la règle 5763 (SSH Brute Force).
    ```xml
<command> 
  <name>glpi_ticket</name> 
  <executable>glpi_ticket.sh</executable>
  <expect>none</expect>
  <timeout_allowed>yes</timeout_allowed>
</command>

<active-response>
  <command>glpi_ticket</command>
  <location>server</location>
  <rules_id>5763</rules_id>
  <timeout>60</timeout>
</active-response>
    ```
    * Redémarrez le manager Wazuh : `systemctl restart wazuh-manager`[cite: 3345].

4.  **Test Final :**
    * Effectuez une attaque Brute Force SSH (règle 5763) avec la Kali.
    * Vérifiez que le ticket incident est créé automatiquement dans GLPI.

### Étape 10: Gestion des Tickets Incidents (GLPI)

1.  Connectez-vous à GLPI avec le compte administrateur `glpi` pour vérifier les droits ou avec le compte `SOC-N1`.
2.  Testez les actions de gestion des incidents sur les tickets générés (réponse, escalade, clôture).

---

## 📚 Conclusion et Références

Ce TP a permis de déployer une solution de sécurité de bout en bout, associant **Wazuh (SIEM/XDR)** à la traçabilité et l'organisation offertes par **GLPI (ITSM)**. L'automatisation de la création de tickets via l'API est essentielle pour accélérer la gestion des incidents de sécurité au sein du SOC.

### Références
* Documentation Wazuh : `https://documentation.wazuh.com/current/quickstart.html`
* Tutoriels spécifiques Wazuh (Active Response, Teler, Suricata).
* Tutoriel Alertes GLPI : (Chapitre III).