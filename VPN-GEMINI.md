# Établissement d'un VPN OpenVPN avec OPNsense et Authentification LDAP

## 📝 Introduction & Objectif

Ce Travail Pratique (TP) vise à configurer un **Serveur OpenVPN** sur le routeur pare-feu **OPNsense** pour fournir un accès sécurisé et chiffré au réseau interne de l'entreprise **SODECAF** aux utilisateurs nomades. La solution utilise **OpenVPN**, un protocole libre, et sera initialement mise en œuvre avec une **PKI (Infrastructure à Clés Publiques)** pour l'authentification des certificats, avant de migrer vers l'**authentification LDAP** via le serveur **Active Directory (SRV-AD1)**. 

**Objectifs Clés :**
1.  Configurer OPNsense en tant que serveur OpenVPN.
2.  Mettre en place la PKI (CA, certificats serveur et client).
3.  Tester l'accès chiffré au réseau interne (SRV-WEB).
4.  Intégrer l'authentification des utilisateurs via **LDAP** à l'Active Directory.

---

## ⚙️ Prérequis (Matériel, Logiciel, Connaissances)

### Composants de l'Infrastructure Virtuelle
* **Routeur Pare-feu :** **OPNsense**.
* **Serveur AD/DNS/DHCP :** **SRV-AD1** (Windows Server).
* **Serveur Web :** **SRV-WEB** (VM).
* **Client Nomade :** **PC client** (VM Windows pour le test VPN).

### Adresses Réseau de l'Infrastructure
| Réseau | Plage d'Adresses | Description / Composants |
| :--- | :--- | :--- |
| **LAN SODECAF** | `172.16.0.0/24` | Réseau Local interne de l'entreprise. |
| **DMZ** | `192.168.0.0/24` | Zone démilitarisée hébergeant SRV-WEB. |
| **WAN (SIO)** | `172.17.0.0/16` | Simule Internet. |
| **VLAN VPN** | `10.0.0.0/24` | Plage d'adresses pour les clients VPN. |

---

## 🛠️ Étapes Détaillées de Mise en Œuvre

### Étape 1: Préparation Initiale d'OPNsense

1.  **Importez** les machines virtuelles nécessaires au montage de l'infrastructure.
2.  **Activez l'interface d'administration web sur l'interface LAN uniquement**. Ceci libère le port TCP 443 côté WAN pour le VPN.
    * **Menu :** `Système` > `Paramètres` > `Administration` > `Interfaces d'écoute`.

### Étape 2: Configuration de la PKI (Certificats)

#### Étape 2.1: Création de l'Autorité de Certification (CA)
* **Menu :** `Système` > `Gestion des certificats` > `Autorités`.
    * Créez une nouvelle CA nommée par exemple `CA-SODECAF`.

#### Étape 2.2: Création du Certificat Serveur
* Créez un certificat interne pour le serveur VPN, signé par la CA `CA-SODECAF`.
    * **Menu :** `Système` > `Gestion des certificats` > `Certificats`.
    * **Nom :** `Sodecaf-VPN-Cert`.

#### Étape 2.3: Création de l'Utilisateur de Test et de son Certificat (Initial)
* Créez un utilisateur pour le test initial du VPN.
    * **Menu :** `Système` > `Accès` > `Utilisateurs`.
    * **Nom :** `Flore Diaz`.
* Créez un certificat pour cet utilisateur, signé par la CA `CA-SODECAF`.
    * **Menu :** `Système` > `Gestion des certificats` > `Certificats`.

### Étape 3: Configuration de l'Instance OpenVPN (PKI Requise)

Configurez l'instance du serveur OpenVPN.

* **Menu :** `VPN` > `OpenVPN` > `Instances`.

| Réglage | Valeur |
| :--- | :--- |
| **Rôle** | `Serveur` |
| **Description** | `VPN client nomade Sodecaf` |
| **Activé** | `✓` |
| **Protocole** | `TCP (IPv4)` |
| **Port number** | `443` |
| **Type** | `TUN` |
| **Server (IPv4)** | `10.0.0.0/24` |
| **Certificat** | `Sodecaf VPN-Cert` |
| **Vérifier le certificat du client** | `requis` |
| **Profondeur du Certificat** | `Ne Pas Vérifier` |
| **Authentification** | `Local Database` |
| **Réseau Local** | `192.168.0.0/24` |
| **Réseau Distant** | `Aucun` (ou laisser vide) |

### Étape 4: Exportation et Test du Client (Mode Certificat/Local)

1.  **Configurez l'export de la configuration :**
    * **Menu :** `VPN` > `OpenVPN` > `Exporter le client`.

| Réglage | Valeur |
| :--- | :--- |
| **Serveur d'Accès Distant** | `VPN client nomade Sodecaf tcp4:443` |
| **Type d'exportation** | `Archiver` |
| **Nom d'hôte** | `192.168.1.43` (Adresse WAN d'OPNsense) |
| **Port** | `443` |
| **Utiliser un port local aléatoire** | `✓` |
| **Valider le sujet du serveur** | `✓` |

2.  **Téléchargez** les fichiers de configuration de `Flore Diaz` (fichier **.ovpn** et fichier **.p12** - certificat de l'utilisateur).
3.  **Installation et Connexion Client :**
    * Installez **OpenVPN client** sur la VM Windows.
    * Déposez le fichier certificat de l'utilisateur (**.p12**) dans le dossier : `c:\users\Nom\OpenVPN\Config\`.
    * Importez le fichier **.ovpn** et testez la connexion.

### Étape 5: Configuration de l'Authentification LDAP

#### Étape 5.1: Configuration du Serveur LDAP (Active Directory)
* **Menu :** `Système` > `Accès` > `Serveurs`.

| Réglage | Valeur |
| :--- | :--- |
| **Nom descriptif** | `LDAP_SODECAF` |
| **Type** | `LDAP` |
| **Nom d'hôte ou adresse IP** | `172.16.0.1` (Adresse de SRV-AD1) |
| **Numéro de port** | `389` |
| **Transport** | `TCP - Standard` |
| **Version du protocole** | `3` |
| **Identités de liaison** | DN de l'utilisateur: `opnsense-ldap` |
| **Étendue de la recherche** | `Sous-arborescence Complète` |
| **DN de Base** | `dc=sodecaf,dc=local` |
| **Conteneurs d'authentification** | `OU=Admins,OU=Employés_sodecaf,DC=sodecaf,...` |
| **Attribut de nom d'utilisateur** | `samAccountName` |

* **Test de Connexion :** Validez la configuration LDAP.
    * **Menu :** `Système` > `Accès` > `Tester`.

#### Étape 5.2: Modification de l'Instance OpenVPN (LDAP)
* **Menu :** `VPN` > `OpenVPN` > `Instances` > `Editer`.
    * **Vérifier le certificat du client :** `aucun(e)`.
    * **Authentification :** `LDAP_SODECAF`.

### Étape 6: Nouvelle Exportation et Test Client (Mode LDAP)

1.  **Nouvelle Exportation :** Exportez la nouvelle configuration client.
    * **Menu :** `VPN` > `OpenVPN` > `Exporter le client`.
    * Choisissez la configuration pour le certificat `Sodecaf-VPN-Cert` (configuration sans vérification de certificat par utilisateur).
2.  **Test de Connexion :** Importez le nouveau fichier de configuration sur le client Windows et refaites le test de connexion. L'utilisateur s'authentifie désormais avec ses identifiants Active Directory.

---

## 🚀 Vérification et Validation (Attaques/Tests)

1.  **Accès Sécurisé :**
    * Vérifiez que l'utilisateur peut accéder au site web (SRV-WEB) via le tunnel VPN.
    * Testez une connexion `ssh` avec le serveur (SRV-WEB).
    * **Intervenez sur le pare-feu d'OPNsense si besoin** pour autoriser le trafic VPN vers la DMZ.
2.  **Analyse de Trames :**
    * Utilisez un outil d'analyse (ex: Wireshark) pour capturer les trames entre le collaborateur (PC client) et l'entreprise.
    * **Protocole et Port :** Indiquez le protocole de transport et le numéro de port utilisé (`TCP` sur le port `443` dans ce cas).
    * **Démontrez le chiffrement :** Montrez que l'échange de données est bien sécurisé (chiffré).

---

## 📚 Conclusion et Références

Ce TP a couvert le déploiement d'un service **OpenVPN** robuste sur **OPNsense**, en passant de l'authentification par **certificats clients** à une méthode centralisée via **LDAP** pour les utilisateurs d'Active Directory. La solution assure un accès distant **chiffré et sécurisé** aux ressources de l'entreprise SODECAF.

### Références
* Documentation Officielle OPNsense
* Manuel OPNsense - Configuration Utilisateur LDAP (Exemple) : `https://docs.opnsense.org/manual/how-tos/user-Idap.html`