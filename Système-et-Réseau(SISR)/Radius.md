# TP Authentification 802.1x et serveur Radius

## Contexte de travail

Nous travaillons sur le contexte de la SODECAF. Votre objectif est de mettre en place une authentification, sécurisée et centralisée, utilisant la solution PacketFence, pour les connexions sans-fils et filaires.

### Topologie Réseau

- **SODECAF Domaine:** `sodecaf.local`
- **Serveurs (172.16.0.0/24):**
  - `SRV-WIN1`: Windows Server (AD + DNS + DHCP) - `172.16.0.1`
  - `SRV-RADIUS`: PacketFence - `172.16.0.10`
- **OPNsense (Routeur/Firewall):**
  - `VLAN10 (ADMIN)`: 192.168.10.254
  - `VLAN20 (DEV)`: 192.168.20.254
  - `VLAN50 (WIFI)`: 192.168.50.254
  - `Host-only (SERVEURS)`: 172.16.0.254
- **Commutateur Cisco (192.168.10.200):**
  - Ports 1 à 4: vlan ADMIN
  - Ports 5 à 8: vlan DEV
  - Ports 13 à 16: vlan WIFI
  - Ports 23 à 24: trunk
- **Point d'accès D-link DAP1665 (192.168.50.200):**
  - `VLAN WIFI`: 192.168.50.0/24

---

## Travail à réaliser

### 1. Configuration du routeur pare-feu OPNsense

- **Faîtes un snapshot avant de modifier la configuration d'OPNsense.**
- Modifiez la configuration d'OPNsense, afin de gérer les VLAN ADMIN, DEV et WIFI sur l'interface 2.5G Intel Ethernet Controler I225-LM. Cette interface gère les tags de VLAN sur les trames (protocole 802.1q).
- Configurez le pare-feu pour autoriser les protocoles IPv4 ICMP, http, https, dns et radius.

### 2. Configuration du commutateur

- Câblez le commutateur et configurez-le afin de respecter les éléments donnés (vlan, configuration des interfaces, passerelle, adresse de management).

### 3. Configuration des étendues DHCP

- Configurez sur le serveur Windows des étendues DHCP pour les différents vlans :

| VLAN  | Etendue             | Passerelle      | DNS       |
|-------|---------------------|-----------------|-----------|
| ADMIN | 192.168.10.50 à 150 | 192.168.10.254  | 172.16.0.1, 1.1.1.1 |
| DEV   | 192.168.20.50 à 150 | 192.168.20.254  | 172.16.0.1, 1.1.1.1 |
| WIFI  | 192.168.50.50 à 150 | 192.168.50.254  | 172.16.0.1, 1.1.1.1 |

- Testez l'obtention d'une adresse IP par une machine cliente, dans chacun des vlans.

### 4. Configuration de l'annuaire Active Directory

- Créez des Unités d'Organisation (UO) dans Active Directory :
  - `UO Utilisateurs_SODECAF`
    - `Sous-UO Admin`
    - `Sous-UO Dev`
    - `Sous-UO Visiteurs`
    - `Sous-UO Services`
- Créez des groupes de sécurité dans chaque UO :
  - `Groupe_Admin` (dans UO Admin)
  - `Groupe_Dev` (dans UO Dev)
  - `Groupe_Visiteurs` (dans UO Visiteurs)
- Créez des comptes utilisateurs pour chaque groupe :
  - `Admin`: uadmin1, uadmin2 (membres de Groupe_Admin)
  - `Dev`: udev1, udev2 (membres de Groupe_Dev)
  - `Visiteurs`: uguest1, uguest2 (membres de Groupe_Visiteurs)
- Créez un compte utilisateur `packetfence` pour la liaison entre PacketFence et l'AD, dans l'UO `Services`.
- Pour chaque utilisateur, autorisez l'accès réseau dans les propriétés des comptes : onglet "Appel entrant" ou "Dial-in". Sélectionnez "Autoriser l'accès".

### 5. Installation et configuration de PacketFence

**Objectif :** Déployer un serveur PacketFence jouant le rôle de serveur RADIUS et de NAC.

- Créez une VM Linux pour PacketFence :
  - **OS recommandé :** Debian 12
  - **RAM :** minimum 4 Go (8 Go recommandés pour production)
  - **CPU :** 2 CPU minimum
  - **Disque :** 50 Go
  - **Interface réseau :** 1 interface en mode bridge
- Configurez l'adresse IP fixe de la VM :
  - **IP :** 172.16.0.10
  - **Masque :** 255.255.255.0 (/24)
  - **Passerelle :** 172.16.0.253 (routeur)
  - **DNS :** 172.16.0.1 (SRV-WIN1)
- Synchronisez la VM avec le même serveur NTP que le serveur Windows.
- En utilisant le [guide d'installation](https://packetfence.org/doc/PacketFence_Installation_Guide.html#_debian_12_system_preparation), installez PacketFence. Le royaume Kerberos par défaut : `SODECAF.LOCAL`.
- Lancez l'assistant de configuration en accédant à l'interface : `https://172.16.0.10:1443`. Suivez l'assistant de configuration initiale.
- **Faîtes un snapshot post-installation.**

### 6. Liaison de PacketFence à l'Active Directory

**Objectif :** Permettre l'authentification 802.1X des utilisateurs AD via PacketFence.

1.  Accédez à l'interface Web de PacketFence et connectez-vous.
2.  Ajoutez une source d'authentification Active Directory : `Configuration` → `Politiques et contrôle d'accès` → `Sources d'authentification`.
3.  Cliquez sur "Nouvelle source interne" et configurez :
    - **Type :** "Active Directory"
    - **Nom :** AD_SODECAF
    - **Host :** 172.16.0.1 (ou sodecaf.local)
    - **Base DN :** `DC=sodecaf,DC=local`
    - **Attribut du nom d'utilisateur :** `sAMAccountName`
    - **Bind DN :** `CN=packetfence,OU=Services,OU=Utilisateurs_SODECAF,DC=sodecaf,DC=local`
    - **Password :** mot de passe compte packetfence
    - **Connection type :** LDAP
4.  Testez la connexion avec le bouton "Test".

### 7. Synchronisation du serveur de temps Windows (srv-win)

**Objectif :** Configurer `srv-win` pour se synchroniser avec le serveur NTP `ntp.univ-rennes2.fr`.

1. **Ouvrir une invite de commande** en tant qu'administrateur sur le serveur Windows (`srv-win`).

2. **Configurer le serveur de temps NTP** en exécutant la commande suivante :
   
   ```cmd
   w32tm /config /manualpeerlist:"ntp.univ-rennes2.fr" /syncfromflags:manual /update
   ```

3. **Arrêter le service de temps Windows :**
   
   ```cmd
   net stop w32time
   ```

4. **Redémarrer le service de temps Windows :**
   
   ```cmd
   net start w32time
   ```

5. **Forcer la resynchronisation immédiatement :**
   
   ```cmd
   w32tm /resync
   ```

6. **Vérifier le statut de la synchronisation :**
   
   ```cmd
   w32tm /query /status
   ```

> **Remarque :**
> - Vérifiez que le port UDP 123 n'est pas bloqué en sortie sur le pare-feu.
> - Cette configuration garantit que l'heure du domaine AD est correcte pour l'authentification Kerberos et les autres services dépendant de l'heure exacte.



### 8. Jointure de PacketFence au domaine

**Objectif :** Joindre le serveur au domaine Windows pour permettre l'authentification 802.1X en PEAP-MSCHAPv2.

1.  Dans l'interface PacketFence : `Configuration` → `Politiques et contrôle d'accès` → `Domaines AD`.
2.  Cliquez sur `Add Domain` et renseignez :
    - **Identifiant :** SODECAF
    - **Workgroup :** SODECAF
    - **Domain :** sodecaf.local
    - **FQDN AD :** srv-win1.sodecaf.local
    - **IP AD :** 172.16.0.1
    - **DNS :** 172.16.0.1
    - **OU :** Computers
3.  Vérifiez qu'un objet computer `packetfence` a été ajouté dans l'UO `Computers` de l'AD.
4.  Activez l'authentification NTLM : `Configuration` → `Politiques et contrôle d'accès` → `Realms` → `Auth NTLM`. Choisissez le Domaine `SODECAF` pour `DEFAULT` et `NULL`.
5.  Redémarrez les services `ntlm-auth-pi` et `radiusd-auth`.

### 9. Création des rôles et mapping VLAN

1.  Créez les rôles dans PacketFence (`Configuration` → `Politiques et contrôle d'accès` → `Rôles`):

    - `role_admin`
    - `role_dev`
    - `role_invite`


2.  Configurez les règles de mapping entre groupes AD et rôles (`Configuration` → `Authentication Sources` → `AD_SODECAF` → `Access Rules`):

    - **Regle1-Admin :**

      - **Condition :** `memberOf = CN=Groupe_Admin,OU=Admin,OU=Utilisateurs_SODECAF,DC=sodecaf,DC=local`
      - **Action1 :** Assign role `role_admin`
      - **Action2 :** Durée d'accès `1j`

    - **Regle2-Dev :**

      - **Condition :** `memberOf = CN=Groupe_Dev,OU=Dev,OU=Utilisateurs_SODECAF,DC=sodecaf,DC=local`
      - **Action1 :** Assign role `role_dev`
      - **Action2 :** Durée d'accès `1j`

    - **Regle3-Visiteurs :**

      - **Condition :** `memberOf = CN=Groupe_Visiteurs,OU=Visiteurs,OU=Utilisateurs_SODECAF,DC=sodecaf,DC=local`
      - **Action1 :** Assign role `role_guest`
      - **Action2 :** Durée d'accès `3h`



4.  Vérifiez la correspondance :

    - Les VLAN ID configurés dans les rôles doivent correspondre aux VLAN du commutateur.
    - Configurez le VLAN par défaut (default role) sur le VLAN 50 (Visiteurs).

### 10. Configuration de PacketFence comme serveur RADIUS 802.1X

- Vérifiez l'activation du service `radiusd` (`Configuration` → `Configuration du système` → `Services`). Ports par défaut : 1812 (auth) et 1813 (accounting).

- Configurez `PEAP` dans le profil EAP par défaut (`Configuration` → `Configuration du système` → `RADIUS` → `Profils EAP`).

- Configurez les méthodes EAP (`Configuration` → `Politiques et contrôle d'accès` → `Profils de connexion`). Pour le profil, sélectionnez `AD_SODECAF` dans les sources.

### 11. Configuration du point d'accès WiFi (WPA2-Enterprise)

#### a. Déclaration du point d'accès sur le serveur Radius

1.  Déclarez le point d'accès dans PacketFence (`Configuration` → `Policies and Access Control` → `Switches`).

    - **Adresse IP :** 192.168.50.200
    - **Type :** D-Link DWL Access-Point
    - **RADIUS Secret :** Btssio2017

2.  Configurez le TAG du VLAN pour le NAS (le point d'accès).

#### b. Configuration du point d'accès WiFi

1.  Accédez à l'interface Web du point d'accès et configurez son adresse IP dans le VLAN WIFI (192.168.50.200).

2.  Configurez le SSID :

    - **SSID :** SISR-x (x = votre numéro de poste)
    - **Mode de sécurité :** WPA2-Enterprise / 802.1X
    - **Type d'authentification :** RADIUS

3.  Configurez le serveur RADIUS :

    - **IP du serveur RADIUS :** 172.16.0.10
    - **Port :** 1812
    - **Clé secrète :** Btssio2017

4.  Vérifiez et appliquez les modifications.

### 12. Tests et validation WiFi (visiteur)

- Connectez-vous au SSID `SISR-x` avec un compte du groupe Visiteurs (ex : `uguest1`).
- Vérifiez l'authentification :
  - La connexion WiFi doit réussir.
  - Le client doit obtenir une adresse IP dans le VLAN WIFI (192.168.50.x).
- Vérifiez la connectivité réseau : `ping 192.168.50.254`.
- Sur PacketFence, consultez les logs de connexion (`Audit` → `Journal d'audit Radius`) pour l'utilisateur `uguest1`. Vérifiez le rôle attribué (`role_guest`) et le VLAN (50).
- Tentez de vous connecter avec un compte administrateur (ex: `uadmin1`). Vérifiez que le TAG correspond au VLAN10.

### 13. Déclaration du commutateur Cisco 2960 dans PacketFence

- Ajoutez le commutateur comme équipement réseau (`Configuration` → `Network Configuration` → `Switches`):

  - **IP Address :** 192.168.10.200
  - **Description :** Commutateur Cisco 2960 - SODECAF
  - **Type :** Cisco → Catalyst 2960
  - **Mode :** Production
  - **RADIUS Secret :** Btssio2017
  - **Role by VLAN ID :** activé
  - **Roles :** `role_admin: 10`, `role_dev: 20`, `role_invite: 50`

### 14. Activer l'enregistrement des appareils (VLANs Dynamiques)

- Cochez la case `Enregistrer automatiquement les appareils` (`Configuration` -> `Politiques et contrôle d'accès` -> `Profils de connexion` -> `Paramètres` -> cocher `Enregistrer automatiquement les appareils`).

### 15. Configuration 802.1X sur le commutateur Cisco 2960

- Ajoutez la configuration suivante sur le commutateur Cisco 2960 :

```cisco
! Enable AAA
aaa new-model

! Define RADIUS server
radius server PACKETFENCE
 address ipv4 172.16.0.10 auth-port 1812 acct-port 1813
 key Btssio2017

! Create RADIUS server group
aaa group server radius PACKETFENCE_GRP
 server name PACKETFENCE

! 802.1X method lists
aaa authentication dot1x default group PACKETFENCE_GRP
aaa authorization network default group PACKETFENCE_GRP
aaa accounting dot1x default start-stop group PACKETFENCE_GRP

! Enable 802.1X globally
dot1x system-auth-control

! Interface config - Fa0/1 to Fa0/4 (VLAN 10)
interface range FastEthernet0/1 - 4
 description 8021X_WIRED_VLAN10
 switchport mode access
 switchport access vlan 10
 authentication port-control auto
 dot1x pae authenticator
 dot1x timeout tx-period 10
 authentication periodic
 authentication timer reauthenticate server

! Interface config - Fa0/5 to Fa0/8 (VLAN 20)
interface range FastEthernet0/5 - 8
 description 8021X_WIRED_VLAN20
 switchport mode access
 switchport access vlan 20
 authentication port-control auto
 dot1x pae authenticator
 dot1x timeout tx-period 10
 authentication periodic
 authentication timer reauthenticate server
```

- **Vérifiez la configuration :**

```
show dot1x all
show aaa servers
show radius statistics
```

### 16. Configuration d'un PC client (Windows)

1.  Démarrez le service `dot3svc`: `net start dot3svc` en PowerShell.

2.  Dans les propriétés de la carte réseau Ethernet, onglet `Authentification`:

    - Activez l'authentification `IEEE 802.1X`.
    - Méthode d'authentification : `Microsoft : Protected EAP (PEAP)`.
    - **Paramètres :** Décocher la case "Vérifier l'identité du serveur en validant le certificat" et dans le menu `configurer` plus bas, décocher "Utiliser automatiquement mon nom et mon mot de passe Windows d'ouverture de session".
    - **Paramètres supplémentaires :** Choisissez `Authentification utilisateur` et entrez les identifiants dans "Remplacer identification".

### 17. Tests et validation filaire (VLAN dynamique)

#### a. Test avec un compte Admin

1.  Branchez le PC client sur un port de 1 à 4.
2.  Connectez-vous avec un compte Admin (ex : `uadmin1`).
3.  Vérifiez l'authentification :
    - Doit réussir.
    - Le port doit être dans le VLAN ADMIN (VLAN 10).
    - Le client doit obtenir une IP dans la plage 192.168.10.x.
4.  Sur le commutateur, vérifiez que le port est dans le VLAN 10.

    - `show authentication sessions`
    - `show vlan`

5.  Consultez les logs PacketFence pour vérifier l'attribution du `role_admin` et du VLAN 10.
6.  Effectuez le même test avec un mot de passe erroné. L'utilisateur ne doit pas accéder.

#### b. Test avec un compte Dev

1.  Déconnectez-vous et reconnectez-vous avec un compte Dev (ex : `udev1`).
2.  Vérifiez :
    - L'authentification doit réussir.
    - Le port doit être dans le VLAN DEV (VLAN 20).
    - Le client doit obtenir une IP dans la plage 192.168.20.x.
3.  Sur le commutateur et dans PacketFence, vérifiez l'attribution du `role_dev` et du VLAN 20.
