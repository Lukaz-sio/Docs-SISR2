# 🛡️ Installation de DVWA et Préparation pour Wazuh

Ce document détaille l'installation de la machine hôte **SRV-WEB** (sous Debian) et le déploiement de l'application web vulnérable **DVWA** (Damn Vulnerable Web Application), ainsi que la configuration horaire nécessaire avant l'installation de l'agent Wazuh.

---

## 1. ⚙️ Installation du Serveur Web (SRV-WEB)

### 1.1. Configuration de Base de la VM

1.  Importez une VM Debian, renommez-la et configurez son adresse IP.
2.  Vérifiez et appliquez le fuseau horaire **Europe/Paris** si nécessaire :

    ```bash
    timedatectl
    timedatectl set-timezone Europe/Paris
    ```

### 1.2. Configuration et Synchronisation NTP

La synchronisation horaire est essentielle pour la corrélation des logs par Wazuh.

1.  Éditez le fichier de configuration du service de temps :

    ```bash
    nano /etc/systemd/timesyncd.conf
    ```

2.  Ajoutez ou modifiez la section `[Time]` pour utiliser le serveur NTP de l'université de Rennes2 :

    ```ini
    [Time]
    NTP=ntp.univ-rennes2.fr
    ```

3.  Activez le service NTP, redémarrez-le et vérifiez la synchronisation :

    ```bash
    timedatectl set-ntp true
    systemctl restart systemd-timesyncd.service
    timedatectl timesync-status
    ```

---

## 2. 🌐 Installation de DVWA (Damn Vulnerable Web Application)

DVWA est une application PHP/MySQL vulnérable utilisée pour les tests d'intrusion. Le script ci-dessous installera les dépendances nécessaires (`apache2`, `mariadb-server`, `php`).

1.  Installez `curl` :

    ```bash
    apt install curl
    ```

2.  Exécutez le script d'installation de DVWA. **Appuyez sur ENTRÉE sans entrer de mot de passe** lorsque demandé pour la configuration de MariaDB.

    ```bash
    bash -c "$(curl --fail --show-error --silent --location [https://raw.githubusercontent.com/IamCarron/DVWA-Script/main/Install-DVWA.sh](https://raw.githubusercontent.com/IamCarron/DVWA-Script/main/Install-DVWA.sh))"
    ```

### 2.1. Vérification de l'Accès

1.  Vérifiez l'accès à la page DVWA à partir d’un client (ex: Kali Linux) via l'URL (adaptez l'IP) : **`http://192.168.0.1/DVWA`**.

| Rôle | Valeur |
| :--- | :--- |
| **Username** | `admin` |
| **Password** | `password` |

# 🛡️ Installation de WAZUH (SRV-WAZUH)

Cette section couvre la préparation du serveur **SRV-WAZUH** (sous Ubuntu 22.04) en définissant ses paramètres matériels, sa configuration réseau (avec ou sans VLAN via Netplan), et sa synchronisation horaire NTP.

---

## 1. 🖥️ Préparation de la Machine Virtuelle

1.  Importez une VM **Ubuntu 22.04 Server**.
2.  Attribuez **4 Go de RAM** à cette machine.
3.  Renommez cette VM **`SRV-WAZUH`**.

---

## 2. 🌐 Configuration Réseau avec Netplan

Ubuntu utilise **Netplan** pour gérer la configuration IP. Vous devez créer le fichier `/etc/netplan/99_config.yaml` et respecter scrupuleusement l'indentation YAML.

### 2.1. Configuration Statique Standard (SANS VLAN)

Utilisez cet exemple pour une configuration statique simple sur l'interface **`ens33`** (adaptez le nom de l'interface si nécessaire) :

```yml
network:
  version: 2
  renderer: networkd
  ethernets:
    ens33:
      addresses:
        - 172.16.0.7/24
      routes:
        - to: default
          via: 172.16.0.254
      nameservers:
        search: [sodecaf.local]
        addresses: [172.16.0.1, 8.8.8.8]

**AVEC VLAN**

```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    # 1. Configurer l'interface physique (ne doit pas avoir d'adresse IP)
    eth0:
      dhcp4: no
      dhcp6: no
  
  vlans:
    # 2. Créer la sous-interface VLAN (nom standard: <interface>.<vlan_id>)
    eth0.10:
      # L'interface physique sur laquelle ce VLAN est taggé
      link: eth0
      # L'ID du VLAN
      id: 10
      # Adresses IP souhaitées pour ce VLAN
      addresses: [192.168.10.50/24]
      routes:
        # Définir la passerelle par défaut (gateway) pour ce VLAN
        - to: default
          via: 192.168.10.1
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
```

· Appliquez cette configuration à l’aide de la commande netplan apply.
· Synchronisez votre serveur WAZUH sur le même serveur NTP que le serveur web.
```bash
timedatectl
timedatectl set-timezone Europe/Paris
```

· Synchronisez votre serveur web sur un serveur NTP, dans le fichier `/etc/systemd/timesyncd.conf`.

```bash
[Time]
NTP=ntp.univ-rennes2.fr
```

· Activez NTP, redémarrez le service et vérifiez la synchronisation.

```bash
timedatectl set-ntp true
systemctl restart systemd-timesyncd.service
timedatectl timesync-status
```

**EFFECTUEZ UNE SNAPSHOT DE VOTRE WAZUH**

Un problème de partition peut survenir, pour être sûr, tapez en console cette commande :

```bash
lvextend -r -l +100%FREE /dev/mapper/ubuntu--vg-ubuntu--lv
```

· Téléchargez et exécutez le script d’installation de Wazuh avec la commande :

```bash
curl -sO https://packages.wazuh.com/4.12/wazuh-install.sh && sudo bash ./wazuh-install.sh -a
```

Accédez à l’interface web de Wazuh à l’adresse https://@IP_wazuh/. 
Le compte administrateur a pour login admin et le mot de passe est celui affiché en console à la fin de l’installation.

Si vous perdez le mot de passe admin, vous pouvez, en console, afficher les mots de passe des utilisateurs à l’aide de la commande :

```bash
sudo tar -O -xvf wazuh-install-files.tar wazuh-install-files/wazuh-passwords.txt
```

Vous pouvez aussi modifier le mot de passe admin :

```bash
cd /usr/share/wazuh-indexer/plugins/opensearch-security/tools
bash wazuh-passwords-tool.sh -u admin -p password
```

créez une nouvelle règle dans Stormshield :

| Status | Action | Source | Destination | Dest. Port |
| :---: | :---: | :---: | :---: | :---: |
| ON | PASS | ANY | SRV-WAZUH | 1514, 1515 |

Maintenant que votre installation de Wazuh est prête, vous pouvez commencer à déployer l’agent Wazuh.

Dans Wazuh, allez dans `Deploy New Agent`, selectionner votre OS et mettez l'adresse IP de votre Wazuh dans Server address. Pas besoin de mettre un agent name.

Copier la commande donnée dans la partie 4 et 5.

Pour Debian : 

```bash
wget https://packages.wazuh.com/4.x/apt/pool/main/w/wazuh-agent/wazuh-agent_4.12.0-1_amd64.deb && sudo WAZUH_MANAGER='172.16.0.7' dpkg -i ./wazuh-agent_4.12.0-1_amd64.deb
```

Redémarrez les services :

```bash
sudo systemctl daemon-reload
sudo systemctl enable wazuh-agent
sudo systemctl start wazuh-agent
```

Pour Windows, lancez powershell en administrateur :

```powershell
Invoke-WebRequest -Uri https://packages.wazuh.com/4.x/windows/wazuh-agent-4.12.0-1.msi -OutFile $env:tmp\wazuh-agent; msiexec.exe /i $env:tmp\wazuh-agent /q WAZUH_MANAGER='172.16.0.7' 
```

Démarrer le service :

```powershell
NET START WazuhSvc
```

Vérifiez que les hôtes apparaîssent sur le dashboard de Wazuh.

# Test d’attaque brute force sur SSH

Sur le serveur Wazuh, ouvrez le fichier `/var/ossec/etc/ossec.conf` et vérifiez la présence des lignes ci-dessous :

```xml
<command>
<name>firewall-drop</name>
<executable>firewall-drop</executable>
<timeout_allowed>yes</timeout_allowed>
</command>
```

Dans ce même fichier, il est possible d’ajouter des réponses actives, qui configurent des réponses automatiques à des
événements relevés par Wazuh.

Attention : la commande firewall-drop utilise iptables. Le paquet iptables doit donc être installé sur la machine agent (ici le serveur web).

```bash
apt install iptables
```

Ajoutez alors le bloc ci-dessous au fichier /var/ossec/etc/ossec.conf :

```xml
<active-response>
<command>firewall-drop</command>
<location>local</location>
<rules_id>5763</rules_id>
<timeout>180</timeout>
</active-response>
```

Enregistrez le fichier modifié. Redémarrez le service wazuh-manager.

Effectuez un test de connectivité de la Kali vers le serveur web.

Sur la Kali Linux, lancez l’attaque par force brute du service SSH :

```bash
hydra -t 4 -l etudiant -P /usr/share/wordlists/rockyou.txt.gz 192.168.0.1 ssh
```

Sur l'interface web de Wazuh, allez dans Threat Hunting puis Events et vérifiez qu'il y a bien un évènement d'attaque `sshd: bruteforce trying to get access to the system` et que l'hôte a bien été bloqué par firewall-drop.

Sur le dashboard de Wazuh, allez que l’agent du SRV-WEB, puis Threat Hunting et appliquez le filtre rule.id is 5763. L’attaque par brute force a été détectée.

Ici une attaque avec l’identifiant MITRE T1110 a été détecté, il s’agit du code attribué par le MITRE pour les attaques de type brute force : https://attack.mitre.org/techniques/T1110/
– rule_id 5763 est la règle de détection brute force SSH dans Wazuh
– Elle correspond à la technique MITRE T1110 – Brute Force.
– L’active response applique automatiquement un blocage temporaire de l’IP attaquante.

# Désactivation d’un compte utilisateur Linux

Add the rule below to the Wazuh server /var/ossec/etc/rules/local_rules.xml file:

```xml
<group name="pam,syslog,">
  <rule id="120100" level="10" frequency="3" timeframe="120">
    <if_matched_sid>5503</if_matched_sid>
    <description>Possible password guess on $(dstuser): 3 failed logins in a short period of time</description>
    <mitre>
      <id>T1110</id>
    </mitre>
  </rule>
</group>
```

Open the Wazuh server /var/ossec/etc/ossec.conf file and verify that a <command> block called disable-account with the following configuration is present within the <ossec_config> block:

```xml
<command>
  <name>disable-account</name>
  <executable>disable-account</executable>
  <timeout_allowed>yes</timeout_allowed>
</command>
```

Add the <active-response> block below to the Wazuh server /var/ossec/etc/ossec.conf configuration file:

```xml
  <active-response>
    <disabled>no</disabled>
    <command>disable-account</command>
    <location>local</location>
    <rules_id>120100</rules_id>
    <timeout>300</timeout>
  </active-response>
```

Redémarrez wazuh-manager :

```bash
sudo systemctl restart wazuh-manager
```

Creéz 2 utilisateurs sur le serveur Web :

```bash
sudo adduser user1
sudo adduser user2
```

Se connecter sur user1 

```bash
su user1
```

Essayer de se connecter au user2 avec le mauvais mot de passe 

```bash
su user2
```

Check that the account was successfully locked using the passwd command:

```bash
sudo passwd --status user2
```

Output

```bash
user2 L 02/20/2023 0 99999 7 -1
```

The L flag indicates the account is locked.

# Détecter des intrusions en utilisant Wazuh et Suricata

Nous allons installer Suricata sur le serveur web SRV-WEB. Il y collectera des informations et les enverra au
manager Wazuh.

```bash
apt update
apt install suricata
```

· On télécharge ensuite des règles par défaut d’inspection des paquets par suricata :

```bash
cd /tmp/ && curl -LO https://rules.emergingthreats.net/open/suricata-6.0.10/emerging.rules.tar.gz
mkdir -p /etc/suricata/rules/
tar -xvzf emerging.rules.tar.gz && sudo mv rules/*.rules /etc/suricata/rules/
chmod 640 /etc/suricata/rules/*.rules
```
  
### Étape 1: Configuration Initiale de Suricata 🔧

1.  **Éditer le fichier de configuration de Suricata** (généralement sous `/etc/suricata/suricata.yaml` ou `/etc/suricata/conf.yaml`).

2.  **Mise à jour des variables réseau et des règles** : Assurez-vous que les lignes suivantes reflètent votre environnement.

    ```yaml
    HOME_NET: "192.168.0.1/24" # Exemple: Mettre ici l'IP ou le CIDR de votre réseau interne
    EXTERNAL_NET: "any"
    rule-files:
    - "*.rules"
    - "/etc/suricata/rules/*.rules"
    # Global stats configuration
    stats:
    enabled: yes
    ```

3.  **Configuration de l'interface de capture** : Localisez la section `af-packet` et remplacez **NOM_INTERFACE** par le nom réel de l'interface réseau de **SRV-WEB** (ex : `eth0`, `ens33`).

    ```yaml
    # Linux high speed capture support
    af-packet:
    - interface: NOM_INTERFACE
    ```

4.  **Redémarrer Suricata** pour appliquer les changements :

    ```bash
    systemctl restart suricata
    ```

### Étape 2: Configuration de l'Agent Wazuh pour Ingestion des Logs 📡

1.  **Modifier le fichier de configuration de l'agent Wazuh** (`/var/ossec/etc/ossec.conf`) sur **SRV-WEB**.

2.  **Ajouter la section `localfile`** pour spécifier le chemin du log et le format JSON :

    ```xml
    <ossec_config>
      <localfile>
        <log_format>json</log_format>
        <location>/var/log/suricata/eve.json</location>
      </localfile>
    </ossec_config>
    ```

3.  **Redémarrer l'agent Wazuh** pour que la nouvelle configuration soit prise en compte :

    ```bash
    systemctl restart wazuh-agent
    ```

### Étape 3: Génération de Trafic de Test 💥

1.  **Sur la machine Kali (Hôte attaquant)**, générez 30 ping vers le serveur web (IP_DE_SRV-WEB).

    ```bash
    ping -c 30 IP_DE_SRV-WEB
    ```

## 🚀 Vérification et Validation (Attaques/Tests)

### Étape 4: Observation des Alertes 👁️

1.  **Sur le SRV-WEB**, observez en temps réel le contenu du fichier de log d'événements de Suricata :

    ```bash
    tail -f /var/log/suricata/eve.json
    ```

2.  **Observation sur le Dashboard Wazuh** : Vérifiez que les alertes ICMP (provenant de Suricata) sont remontées sur l'interface Wazuh Manager pour l'agent SRV-WEB.

# Intégration de Wazuh (SIEM) et GLPI (ITSM) pour la Gestion Automatisée des Incidents de Sécurité

## 📝 Introduction & Objectif
Ce Travail Pratique (TP) vise à automatiser la gestion des incidents de cybersécurité en intégrant le **SIEM Wazuh** avec l'outil **ITSM GLPI**. L'objectif est de configurer une réponse active (Active Response) dans Wazuh qui utilise l'API de GLPI pour créer automatiquement des tickets incidents dès qu'une alerte critique est détectée.

## ⚙️ Prérequis (Matériel, Logiciel, Connaissances)

### Matériel / Machines Virtuelles
* **GLPI Server** : Serveur installé et opérationnel, accessible à l'adresse `http://172.16.0.8/`.
* **Wazuh Manager Server** : Serveur Wazuh configuré.
* **Kali Linux** : Machine utilisée pour générer l'attaque de test.

### Informations de Connexion GLPI
* **URL de connexion** : `http://172.16.0.8/`
* **Compte administrateur** : `identifiant: glpi`, `mot de passe: glpi`

## 🛠️ Étapes Détaillées de Mise en Œuvre

### Étape 1: Préparation de l'Infrastructure et Activation de l'API GLPI

1.  **Importation et connexion aux VMs** :
    * Importez les différentes VM et modifiez les connexions réseaux (LAN SEGMENT) si besoin.
2.  **Connexion à GLPI** :
    * Connectez-vous à l’interface web de GLPI : `http://172.16.0.8/`.
    * Utilisez le compte administrateur (`glpi`/`glpi`).
3.  **Activation de l'API Rest (Interface Web GLPI)** :
    * Activez l’API Rest et activez la connexion avec un jeton externe.
4.  **Création du Client API Wazuh (Interface Web GLPI)** :
    * Ajoutez un client de l’API, **`wazuh_api`**, en indiquant l'adresse IPv4 du serveur Wazuh.
    * Régénérez un **jeton d’application (app\_token)**.
5.  **Création de l'utilisateur API GLPI (Interface Web GLPI)** :
    * Allez dans **Administration > Utilisateurs > Ajouter un utilisateur**.
    * Créez l'utilisateur avec l'identifiant **`wazuh`**. Configurez son fuseau horaire.
6.  **Génération du Jeton Utilisateur (Interface Web GLPI)** :
    * Sélectionnez l'utilisateur **`wazuh`** puis dans la partie **Clefs d’accès distant**, régénérez un **jeton d’API (user\_token)**.
7.  **Sauvegarde** : Enregistrez les deux tokens (**app\_token** et **user\_token**).

### Étape 2: Test de l'API depuis le Serveur Wazuh

Effectuez les tests suivants dans la console Shell du serveur Wazuh. **Remplacez** les valeurs des jetons et de l'IP (`172.16.0.8`) si nécessaire.

1.  **Test d'authentification (initSession)** :

    ```bash
    curl -X GET \
    -H 'Content-Type: application/json' \
    -H "Authorization: user_token insérer_ici_votre_user_token" \
    -H "App-Token: insérer_ici_votre_app_token" \
    '[http://172.16.0.8/apirest.php/initSession?get_full_session=true](http://172.16.0.8/apirest.php/initSession?get_full_session=true)'
    ```

    * **Note :** Si le test est correct, vous recevrez un `session_token`.

2.  **Génération d’un ticket de test (POST /Ticket)** :
    * Utilisez le `session_token` reçu précédemment (ex : `bk6smoi2cj0mgj7i1p22sinakr`).

    ```bash
    curl -X POST \
    -H 'Content-Type: application/json' \
    -H 'Authorization: user_token insérer_ici_votre_user_token' \
    -H 'App-Token: insérer_ici_votre_app_token' \
    -H 'Session-Token: bk6smoi2cj0mgj7i1p22sinakr' \
    -d '{
    "input": {
    "name": "Alerte Wazuh - Test API",
    "content": "Ceci est un ticket créé automatiquement depuis Wazuh via API",
    "priority": 4,
    "urgency": 3,
    "impact": 3,
    "status": 1,
    "type": 1,
    "itilcategories_id": 2
    }
    }' \
    [http://172.16.0.8/apirest.php/Ticket](http://172.16.0.8/apirest.php/Ticket)
    ```

    * Vérifiez la création du ticket sous GLPI.

3.  **Fermeture de la session (killSession)** :

    ```bash
    curl -X GET \
    -H 'Authorization: user_token insérer_ici_votre_user_token' \
    -H 'App-Token: insérer_ici_votre_app_token' \
    -H 'Session-Token: bk6smoi2cj0mgj7i1p22sinakr' \
    [http://172.16.0.8/apirest.php/killSession](http://172.16.0.8/apirest.php/killSession)
    ```

### Étape 3: Mise en place du Script de Réponse Active

1.  **Création du fichier de log et droits** :

    ```bash
    touch /var/log/glpi_ticket.log
    # Adaptez le propriétaire et les droits si nécessaire (root:wazuh recommandé)
    chown root:wazuh /var/log/glpi_ticket.log
    chmod 660 /var/log/glpi_ticket.log
    ```

2.  **Copie et modification du script** :
    * Copiez le code ci-dessous dans le fichier **/var/ossec/active-response/bin/glpi\_ticket.sh** sur le serveur Wazuh.
    * **Remplacez** les valeurs des variables `APP_TOKEN` et `USER_TOKEN`.

    ```bash
    #!/bin/bash
    # Script Active Response Wazuh → GLPI
    # Version améliorée avec logs et mapping gravité → priorité

    GLPI_URL="[http://172.16.0.8/apirest.php](http://172.16.0.8/apirest.php)"
    APP_TOKEN="IbQdjd32WUg5wAJrpQb7ZwnWdyVHLfITNriLrQHy" # À MODIFIER
    USER_TOKEN="wPNzhNzcwZNdabEJFBVzT4xkBg2BnWyZwQhlDWhv" # À MODIFIER

    LOGFILE="/var/log/glpi_ticket.log"

    # Lire tout le JSON d’entrée (multi-lignes possible)
    INPUT_JSON=$(cat)

    ALERT_DATE=$(date '+%Y-%m-%d %H:%M:%S %z')

    echo "$(date) - Script exécuté par Wazuh" >> /var/log/glpi_ticket.log
    echo "$INPUT_JSON" >> /var/log/glpi_ticket.log

    # Extraire infos utiles avec jq
    RULE_ID=$(echo "$INPUT_JSON" | jq -r '.parameters.alert.rule.id')
    RULE_DESC=$(echo "$INPUT_JSON" | jq -r '.parameters.alert.rule.description')
    AGENT_NAME=$(echo "$INPUT_JSON" | jq -r '.parameters.alert.agent.name')
    SRC_IP=$(echo "$INPUT_JSON" | jq -r '.parameters.alert.data.srcip // empty')
    SEVERITY=$(echo "$INPUT_JSON" | jq -r '.parameters.alert.rule.level')
    LOG=$(echo "$INPUT_JSON" | jq -r '.parameters.alert.full_log')

    # Mapping gravité Wazuh (level) → priorité GLPI
    if [ "$SEVERITY" -le 3 ]; then
    PRIORITY=1   # Faible
    elif [ "$SEVERITY" -le 7 ]; then
    PRIORITY=3   # Moyen
    else
    PRIORITY=5   # Critique
    fi

    # Ouvrir une session GLPI
    SESSION_TOKEN=$(curl -s -X GET \
    -H "Authorization: user_token $USER_TOKEN" \
    -H "App-Token: $APP_TOKEN" \
    "$GLPI_URL/initSession" | jq -r '.session_token')

    # Créer le ticket
    RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -H "App-Token: $APP_TOKEN" \
    -H "Session-Token: $SESSION_TOKEN" \
    -d "{
    \"input\": {
    \"name\": \"Alerte Wazuh - $RULE_DESC\",
    \"content\": \"🚨 Alerte Wazuh\n\n- Date alerte : $ALERT_DATE\n- Règle ID : $RULE_ID\n- Description : $RULE_DESC\n- Agent : $AGENT_NAME\n- Source IP : $SRC_IP\n- Gravité : $SEVERITY\n- Log : $LOG\",
    \"priority\": $PRIORITY,
    \"urgency\": 3,
    \"impact\": 3,
    \"status\": 1,
    \"type\": 1,
    \"itilcategories_id\": 2
    }
    }" \
    "$GLPI_URL/Ticket")

    # Fermer la session
    curl -s -X GET \
    -H "App-Token: $APP_TOKEN" \
    -H "Session-Token: $SESSION_TOKEN" \
    "$GLPI_URL/killSession" > /dev/null

    # Log local pour suivi
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Ticket créé : Règle=$RULE_ID, Desc=$RULE_DESC, IP=$SRC_IP, Gravité=$SEVERITY, Priorité=$PRIORITY" >> "$LOGFILE"
    ```

3.  **Modification des droits du script** :

    ```bash
    chown root:wazuh /var/ossec/active-response/bin/glpi_ticket.sh
    chmod 750 /var/ossec/active-response/bin/glpi_ticket.sh
    ```

4.  **Test manuel du script** :

    ```bash
    echo '{"parameters":{"alert":{"rule":{"id":"5710","description":"Tentative brute force SSH","level":10},"agent":{"id":"001","name":"srv-web"},"data":{"srcip":"172.16.0.50"},"full_log":"sshd failed login"}}}' | /var/ossec/active-response/bin/glpi_ticket.sh
    ```

    * Un ticket doit être créé sur GLPI.

### Étape 4: Configuration de la Réponse Active Wazuh

1.  **Modification du fichier de configuration du Wazuh Manager** (`/var/ossec/etc/ossec.conf`) :
    * Ajoutez la définition de la commande :

    ```xml
    <command>
      <name>glpi_ticket</name>
      <executable>glpi_ticket.sh</executable>
      <expect>none</expect>
      <timeout_allowed>yes</timeout_allowed>
    </command>
    ```

    * Ajoutez la règle de réponse active pour la Rule ID **5763** (attaque ssh):

    ```xml
    <active-response>
      <command>glpi_ticket</command>
      <location>server</location>
      <rules_id>5763</rules_id>
      <timeout>60</timeout>
    </active-response>
    ```

2.  **Redémarrage du service Wazuh Manager** :

    ```bash
    systemctl restart wazuh-manager
    ```

## 🚀 Vérification et Validation (Attaques/Tests)

1.  **Lancement de l'attaque** :
    * Avec la machine Kali Linux, effectuez une attaque sur le service ssh du serveur cible (DVWA/SRV-WEB).

2.  **Vérification de la création du ticket** :
    * Vérifiez la bonne création du ticket incident sur GLPI.

## 📚 Conclusion et Références

* **Gestion des tickets incidents** : Connectez-vous avec le compte **SOC-N1** et testez la gestion de ces tickets incidents (réponse, escalade, clôture).







































