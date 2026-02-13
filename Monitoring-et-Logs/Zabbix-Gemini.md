# Supervision Complète de l'Infrastructure SODECAF avec Zabbix

## 📝 Introduction & Objectif

Ce Travail Pratique (TP) vise à mettre en place une solution de **supervision professionnelle libre de droit, Zabbix**, au sein de l'infrastructure réseau de l'entreprise SODECAF. La supervision est essentielle pour surveiller, rapporter et alerter sur le bon fonctionnement des systèmes et des services informatiques.

**Objectifs du TP :**
1.  **Installer et paramétrer** le serveur Zabbix 6.0 sur une VM Debian 12 **sans accès Internet**.
2.  Superviser les hôtes critiques de l'infrastructure : **SRV-AD1, SRV-WEB1 et OPNsense**, en utilisant les agents Zabbix et le protocole **SNMP**.
3.  Mettre en place des **déclencheurs** (Triggers) pour détecter des anomalies.
4.  Configurer les **notifications par e-mail (Gmail)** pour alerter l'administrateur.
5.  Créer une **cartographie** pour une visualisation rapide de l'état du réseau.



---

## ⚙️ Prérequis (Matériel, Logiciel, Connaissances)

### Infrastructure SODECAF
L'infrastructure utilise le schéma suivant :
* **SRV-ZABBIX :** VM **Debian 12** (IP : `172.16.0.5`), 2 Go de RAM.
* **SRV-AD1 :** VM Windows Server (AD, DNS, DHCP) (IP : `172.16.0.1` - supposée).
* **SRV-WEB1 :** VM (Web Server).
* **OPNsense :** Routeur pare-feu (LAN IP : `172.16.0.254`).
* **Réseau LAN :** `172.16.0.0/24`.

### Logiciel et Outils
* Image VM **Debian 12** (pour Zabbix Server).
* Images VM **Windows Server** et **VM Web**.
* Accès aux fichiers d'installation de Zabbix (paquets `.deb` ou iso/dossier local contenant les dépôts).
* Compte **Gmail** (pour les alertes).
* Client SSH/Console pour les commandes sur SRV-ZABBIX.

---

## 🛠️ Étapes Détaillées de Mise en Œuvre

### Étape 1: Installation et Configuration du Serveur Zabbix (Mode Hors Ligne)

**⚠️ ATTENTION : Ces commandes supposent que vous avez déjà accès à un dépôt local ou aux fichiers `.deb` sur votre machine virtuelle SRV-ZABBIX, car vous n'avez pas d'accès à Internet. Les commandes ci-dessous visent à reproduire la séquence d'installation officielle pour Zabbix 6.0 LTS sur Debian 12 (Bookworm) avec MySQL/Apache, mais nécessiteront que les paquets soient disponibles localement.**

1.  **Préparation de la VM Zabbix :**
    * Importez la VM Debian 12.
    * Attribuez **2 Go de RAM** à la machine virtuelle et configurez son adresse IP (`172.16.0.5`).

2.  **Installation des Paquets (Préparation locale) :**

    * **Scenario 1: Paquets `.deb` disponibles localement (Recommandé) :**
        * Si vous avez téléchargé le paquet de dépôt et les paquets Zabbix principaux sur un support (clé USB, dossier partagé), installez-les dans l'ordre. Remplacez `[chemin]` par l'emplacement réel de vos fichiers.

        ```bash
        # 1. Installation du paquet de dépôt Zabbix :
        wget https://repo.zabbix.com/zabbix/7.4/release/debian/pool/main/z/zabbix-release/zabbix-release_latest_7.4+debian12_all.deb
        dpkg -i [chemin]/zabbix-release_latest_7.4+debian12_all.deb

        # 2. Mise à jour des index de paquets locaux
        apt update

        # 3. Installation du serveur, du frontend (Apache) et des dépendances MySQL
        # Si 'apt install' échoue faute de réseau, vous devrez installer manuellement toutes les dépendances.
        # En supposant que vous avez un cache APT ou une ISO montée :
        apt install zabbix-server-mysql zabbix-frontend-php zabbix-apache-conf zabbix-sql-scripts zabbix-agent
        ```

    * **Scenario 2: Installation manuelle du serveur MySQL (si `apt install` échoue pour MySQL) :**
        ```bash
        # Installation manuelle de MySQL Server (si non installé)
        apt install mysql-server -y
        ```

3.  **Configuration de la Base de Données MySQL :**

    ```sql
    # Connexion à MySQL et création de la base de données
    # (Utiliser le compte root de MySQL si un mot de passe a été défini lors de l'installation, sinon pas de -p)
    mysql -uroot -p

    # Une fois dans la console MySQL :
    CREATE DATABASE zabbix character set utf8mb4 collate utf8mb4_bin;
    CREATE USER 'zabbix'@'localhost' IDENTIFIED BY 'votre_mot_de_passe_db';
    GRANT ALL PRIVILEGES ON zabbix.* TO 'zabbix'@'localhost';
    FLUSH PRIVILEGES;
    set global log_bin_trust_function_creators = 1;
    quit;
    ```

4.  **Importation du Schéma de Base de Données Zabbix :**

    ```bash
    # Importation du schéma (le chemin dépend de la version de Zabbix installée)
    zcat /usr/share/zabbix/sql-scripts/mysql/server.sql.gz | mysql --default-character-set=utf8mb4 -uzabbix -p zabbix 
    ```

5.  **Désactivation de l'option log_bin_trust_function_creators :**

    ```sql
    mysql -uroot -p password
    mysql> set global log_bin_trust_function_creators = 0;
    mysql> quit; 
    ```

5.  **Configuration du Serveur Zabbix :**

    * Modifiez le fichier de configuration du serveur Zabbix (`/etc/zabbix/zabbix_server.conf`) :
    ```bash
    nano /etc/zabbix/zabbix_server.conf
    ```
    * Décommentez et définissez les paramètres de la base de données (remplacez `votre_mot_de_passe_db`) :
        ```conf
        DBHost=localhost
        DBName=zabbix
        DBUser=zabbix
        DBPassword=votre_mot_de_passe_db
        ```

6.  **Redémarrage des Services :**

    ```bash
    # Redémarrage du serveur MySQL
    systemctl restart mysql

    # Redémarrage du serveur Zabbix
    systemctl restart zabbix-server zabbix-agent apache2

    # Activation des services au démarrage
    systemctl enable zabbix-server zabbix-agent apache2
    ```

7.  **Configuration Web de Zabbix (via navigateur http://172.16.0.5/zabbix) :**

    * **Vérification des prérequis :** Vérifiez que tous les paquets logiciels nécessaires sont bien installés (PHP et ses modules).
    * **Configuration de la Connexion à la Base de Données :**
        * Hôte base de données : `localhost`
        * Port de la base de données : `0`
        * Nom de la base de données : `zabbix`
        * Utilisateur : `zabbix`
        * Mot de passe : `votre_mot_de_passe_db`
    * **Paramètres du Serveur :**
        * Nom du serveur Zabbix : `srv-zabbix`
        * Fuseau horaire par défaut : `(UTC+01:00) Europe/Paris`
    * **Connexion :** À la fin de l'installation, connectez-vous avec le compte par défaut :
        * Nom d'utilisateur : `Admin`
        * Mot de passe : `zabbix`

---

### Étape 2: Supervision du SRV-AD1 (DHCP et DNS)

#### Étape 2.1: Configuration via Zabbix Agent (CPU/Mémoire)

1.  **Installation de l'Agent Zabbix sur SRV-AD1 :**
    * Installez sur le serveur AD l'agent 2 Zabbix.
    * Configurez les paramètres de l'agent :

| Champ | Valeur |
| :--- | :--- |
| Host name : | `SRV-AD1` |
| Zabbix server IP/DNS : | `172.16.0.5` |
| Agent listen port : | `10050` |
| Server or Proxy for active checks : | `127.0.0.1` |

2.  **Ajout de l'Hôte dans Zabbix :**
    * **Menu :** `Configuration` > `Hôtes` > `Créer un hôte`.
    * **Modèle :** Ajoutez le modèle `Windows by Zabbix Agent`.
    * Vérifiez le bon fonctionnement en supervisant, par exemple, le taux d'utilisation de la mémoire et du processeur.

#### Étape 2.2: Supervision DHCP via SNMP

1.  **Installation et Activation de SNMP sur SRV-AD1 :**
    * Installez et activez le service SNMP sur Windows server 2022 en utilisant le tutoriel à ce lien `https://www.it-connect.fr/configurer-snmp-sous-windows-server-2012-r2/`.

2.  **Création d'un Élément SNMP (Adresses DHCP Libres) :**
    * L'OID pour le nombre d'adresses disponibles (`noAddFree`) pour le sous-réseau `172.16.0.0` est : `1.3.6.1.4.1.311.1.3.2.1.1.3.172.16.0.0`
    * **Menu :** `Configuration` > `Hôtes` > `Éléments` (sur `SRV-AD1`) > `Créer un élément` (`DhcpNoAddFree`).

| Champ | Valeur |
| :--- | :--- |
| Nom | `DhcpNoAddFree` |
| Type | `Agent SNMP` |
| Clé SNMP OID | `1.3.6.1.4.1.311.1.3.2.1.1.3.172.16.0.0` |
| Type d'information | `Numérique (non signé)` |
| Interface hôte | `172.16.0.1` |
| Période de stockage de l'historique | `90d` |

3.  **Vérification :** Vérifiez la bonne remontée de nouvelles informations sur le service DHCP.
4.  **Test :** Faites le test en activant et désactivant le service DHCP du serveur SRV-AD1.

#### Étape 2.3: Supervision DNS via Agent Zabbix (Test de résolution)

1.  **Création d'un Élément DNS (Test de résolution) :**
    * **Menu :** `Configuration` > `Hôtes` > `Éléments` (sur `SRV-AD1`) > `Créer un élément`.

| Champ | Valeur |
| :--- | :--- |
| Nom | `Test de requête DNS` |
| Type | `agent Zabbix` |
| Clé | `net.dns[172.16.0.1,srv-ad1.sodecaf.local,A,2,1,udp]` |
| Type d'information | `Numérique (non signé)` |
| Interface hôte | `172.16.0.1:10050` |
| Intervalle d'actualisation | `1m` |

2.  **Test :** Faites le test en activant et désactivant le service DNS du serveur SRV-AD1.

---

### Étape 3: Supervision du SRV-WEB1 (Apache)

1.  **Configuration d'Apache (SRV-WEB1) :**
    * Ouvrez le fichier `/etc/apache2/mods-enabled/status.conf` et modifiez la partie ci-dessous pour autoriser l'accès à la page de statut Apache.

```bash
<Location/server-status>
SetHandler server-status
Require ip 127.0.0.1 192.168.0.0/24 172.16.0.0/24
</Location>
```

* Redémarrez ensuite le service Apache2.

2.  **Installation de l'Agent Zabbix sur SRV-WEB1 :**
    * Installez le paquet `zabbix-agent` sur le serveur web.
    * Dans le fichier de configuration `/etc/zabbix/zabbix-agentd.conf`, configurez l'adresse IP du serveur Zabbix.

3.  **Modification du Modèle Zabbix :**
    * **Menu :** `Configuration` > `Modèles` > `Apache by Zabbix Agent` > `Macros`.
    * Modifiez la macro `{$APACHE.PROCESS.NAME}` :

| Macro | Valeur |
| :--- | :--- |
| `{$APACHE.PROCESS.NAME}` | `apache2` |

4.  **Ajout de l'Hôte dans Zabbix :**
    * Ajoutez l'hôte **SRV-WEB1** sur Zabbix avec pour modèle `Apache by Zabbix Agent`.

---

### Étape 4: Supervision du Routeur Pare-feu OPNsense

1.  **Installation des Greffons (Plugins) :**
    * **Menu :** `Système` > `Firmware` > `Greffons`.
    * Ajoutez les greffons **`os-zabbix-agent`** et **`os-net-snmp`**.

2.  **Activation de l'Agent Zabbix :**
    * **Menu :** `Services` > `Agent Zabbix` > `Paramètres`.
    * Activez l'agent et configurez l'IP du serveur Zabbix (`172.16.0.5`).

3.  **Activation de SNMP :**
    * **Menu :** `Services` > `SNMP`.
    * Activez le service SNMP.
    * Communauté SNMP : `sodecaf`.
    * IPs d'écoute : `172.16.0.254`.
    * Sauvegardez.

4.  **Règle de Pare-feu :**
    * Ouvrez le port **UDP 161** sur le pare-feu côté **LAN**.

5.  **Ajout de l'Hôte dans Zabbix :**
    * Ajoutez l'hôte **OPNsense** sous Zabbix avec pour modèles : `FreeBSD by Zabbix Agent` et `OPNsense by SNMP`.

---

### Étape 5: Déclencheurs et Notifications par E-mail

#### Étape 5.1: Création d'un Déclencheur DHCP

1.  **Menu :** `Configuration` > `Hôtes` > `Déclencheurs` (sur `SRV-AD1`) > `Créer un déclencheur`.
    * Nom : `Nombre d'adresses DHCP disponibles trop faible`
    * Sévérité : `Haut`
    * Expression :
```bash
last(/SRV-AD/1.3.6.1.4.1.311.1.3.2.1.1.3.172.16.0.0)<10
```

2.  **Test :** Modifiez l'étendue DHCP sur SRV-AD1 pour provoquer un incident.

#### Étape 5.2: Configuration du Serveur d'Envoi de Mail (ssmtp)

1.  **Installation des paquets sur SRV-ZABBIX :**

```bash
apt install ssmtp mailutils
```

2.  **Configuration de ssmtp :**
    * Ouvrez le fichier `/etc/ssmtp/ssmtp.conf` et modifiez-le :

```conf
root=adressemail@gmail.com
mailhub=smtp.gmail.com:465
hostname=zabbix
FromLineOverride=YES
AuthUser adressemail@gmail.com
AuthPass motdepasse
UseTLS=YES
```

3.  **Création du Script d'Alerte Zabbix :**
    * Créez et éditez le script :
```bash
nano /usr/lib/zabbix/alertscripts/zabbix-sendmail
```
* Contenu du script :
```bash
#!/bin/bash
echo "\$3" | /usr/bin/mail -s "\$2" \$1
```
* Permissions :
```bash
chmod +x /usr/lib/zabbix/alertscripts/zabbix-sendmail
```

#### Étape 5.3: Configuration du Type de Média dans Zabbix (Interface Web)

1.  **Menu :** `Administration` > `Types de média` > `Créer un type de média`.
    * Nom : `Zabbix-sendMail (Gmail)`
    * Type : `Script`
    * Nom du script : `zabbix-sendmail`
    * Paramètres du script : `{[ALERT.SENDTO]}`, `{[ALERT.SUBJECT]}`, `{[ALERT.MESSAGE]}`

2.  **Configuration du Média pour l'Utilisateur Admin :**
    * **Menu :** `Administration` > `Utilisateurs` > `Admin` > `Média` > `Ajouter`.
        * Type : `Zabbix-sendMail (Gmail)`
        * Envoyer à : `adressemail@gmail.com`
        * Utiliser si sévérité : Cochez à partir de **Moyen**.
        * Quand actif : `1-7,00:00-24:00`.

3.  **Activation de l'Action de Déclenchement :**
    * **Menu :** `Configuration` > `Actions` > `Action de déclencheur`.
    * Activez l'action : `Report problems to Zabbix administrators`.

---

### Étape 6: Cartographie du Réseau

1.  **Création de la Carte :**
    * **Menu :** `Surveillance` > `Cartes` > `Éditer la carte`.
    * Créez une carte pour visualiser rapidement les machines et les services supervisées de la SODECAF.



## 📚 Conclusion et Références

Le serveur **Zabbix** est désormais installé et configuré pour superviser les serveurs clés de l'infrastructure SODECAF. La mise en place de **déclencheurs** et d'une **action de notification par e-mail** assure une surveillance proactive. La **cartographie** offre une vue d'ensemble immédiate de la santé du réseau.

### Références
* Tutoriel SNMP Windows Server : `https://www.it-connect.fr/configurer-snmp-sous-windows-server-2012-r2/`