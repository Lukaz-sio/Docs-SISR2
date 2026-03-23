# 📧 Monter son serveur de mails (iRedMail)

**Contexte :**
Les utilisateurs de la SODECAF souhaitent pouvoir échanger entre eux par e-mails. L'objectif est de mettre en place un serveur de messagerie complet permettant d'ajouter ce nouveau service dans l'entreprise, en utilisant la solution **iRedMail**.

iRedMail est une solution open source complète reposant sur les composants suivants :
- **Postfix** (MTA) : Reçoit et envoie les messages, gère le routage SMTP, les files d'attente et applique les règles de filtrage.
- **Dovecot** (IMAP/POP) : Stocke les mails sur le disque, gère l'authentification des utilisateurs et l'accès aux boîtes aux lettres.
- **Roundcube** (Webmail) : Interface web qui s'appuie sur IMAP et SMTP pour lire et envoyer les messages.
- Outils de sécurité : **MariaDB**, **ClamAV** (anti-virus), **SpamAssassin** (anti-spam) et **Fail2Ban**.

---

## 🛠️ 1. Installation et configuration de la VM Debian

1. Importez une nouvelle VM **Debian 12** et augmentez la taille de la mémoire RAM à **4 Go**.
2. Effectuez les mises à jour :
   ```bash
   apt update && apt upgrade -y
   ```
3. Configurez l'adresse IP de ce serveur de mail selon votre schéma réseau (ex: `172.16.0.8`).
4. Renommez le serveur en `iredmail` et modifiez le fichier `/etc/hosts` en l'éditant pour correspondre aux lignes suivantes :
   ```bash
   nano /etc/hosts
   ```
   ```text
   127.0.0.1       localhost
   172.16.0.8      mail.sodecaf.local iredmail
   127.0.1.1       iredmail
   
   # The following lines are desirable for IPv6 capable hosts
   ::1             localhost ip6-localhost ip6-loopback
   ff02::1         ip6-allnodes
   ff02::2         ip6-allrouters
   ```
5. Modifiez le fichier `/etc/resolv.conf` comme suit :
   ```bash
   nano /etc/resolv.conf
   ```
   ```text
   nameserver 172.16.0.1
   search sodecaf.local
   ```

### Installation de iRedMail
Voici les étapes détaillées pour installer iRedMail directement sur votre serveur :

1. **Installer les prérequis** :
   ```bash
   apt-get install -y gzip dialog wget
   ```

2. **Télécharger la dernière version de iRedMail** :
   *(Vérifiez la dernière version sur la [page de téléchargement iRedMail](https://www.iredmail.org/download.html))*
   ```bash
   cd /root
   wget https://github.com/iredmail/iRedMail/archive/refs/tags/1.6.8.tar.gz
   ```

3. **Décompresser l'archive** :
   ```bash
   tar zxf 1.6.8.tar.gz
   ```

4. **Lancer le script d'installation** :
   ```bash
   cd iRedMail-1.6.8/
   bash iRedMail.sh
   ```

Lors de l'installation via les fenêtres interactives de l'assistant, faites les choix suivants :
- **Emplacement des mails** : laissez le dossier par défaut `/var/vmail/`.
- **Backend d'authentification** : choisissez un annuaire **OpenLDAP** pour la liaison future vers le serveur AD.
- **Base de données** : choisissez **MySQL/MariaDB** (un mot de passe d'administration sera généré automatiquement).
- **Nom de domaine** : indiquez votre nom de domaine (ex: `sodecaf.local`).
- **Composants optionnels** : cochez les modules **iRedAdmin**, **Roundcubemail**, et **Fail2ban**.

Une fois toutes les questions répondues, tapez `Y` et faites *Entrée* pour lancer le déploiement automatique. 

Une fois l'installation complètement terminée, **redémarrez** la machine virtuelle iRedMail :
```bash
reboot
```

### Modification des permissions
Une fois le serveur redémarré, modifiez les permissions du dossier contenant les mails :
```bash
chown -R vmail:vmail /var/vmail/
chmod 755 /var/vmail/
chmod 750 /var/vmail/sodecaf.local/ 2>/dev/null || true
```

---

## 🌐 2. Modifications sur le serveur DNS et Active Directory (AD)

Sur le **serveur DNS** de la sodecaf (Windows Server), ajoutez les enregistrements suivants :

1. **Dans la zone de recherche directe** (`sodecaf.local`), ajoutez deux entrées :
   - Hôte (A) : `iredmail` qui pointe vers `172.16.0.8`
   - Serveur de messagerie (MX) : `mail` qui pointe vers `[10] iredmail.sodecaf.local`

2. **Dans la zone de recherche inversée**, ajoutez l'entrée :
   - Pointeur (PTR) : `172.16.0.8` vers `iredmail.sodecaf.local.` (statique)

3. **Dans l'annuaire Active Directory**, créez un compte de service :
   - Nommez l'utilisateur : **`iredmail`** (Ce compte sera utilisé pour les requêtes LDAP).

---

## 🔗 3. Connexion de Dovecot à l’annuaire AD

Le principe : Postfix et Dovecot n'interrogeront pas le LDAP local d'iRedMail mais votre AD Windows. Le compte de service `iredmail` effectuera le Binding LDAP.

1. Sur le serveur iRedMail, faîtes une copie de sauvegarde du fichier :
   ```bash
   cp /etc/dovecot/dovecot-ldap.conf /etc/dovecot/dovecot-ldap.conf.bak
   ```
2. Éditez le fichier `/etc/dovecot/dovecot-ldap.conf` et remplacez le backend pour cibler l'AD :
   ```bash
   nano /etc/dovecot/dovecot-ldap.conf
   ```
   *Contenu à insérer (en adaptant le mot de passe de binding si besoin, ici `Rootsio2017`) :*
   ```ini
   hosts = 172.16.0.1:389
   ldap_version = 3
   auth_bind = yes
   dn = CN=iredmail,OU=Services,OU=Sodecaf,DC=sodecaf,DC=local
   dnpass = Rootsio2017
   base = DC=sodecaf,DC=local
   scope = subtree
   deref = never

   # Required pour doveadm
   iterate_attrs = userPrincipalName=user
   iterate_filter = (&(userPrincipalName=*)(objectClass=person)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))
   user_filter = (&(userPrincipalName=%u)(objectClass=person)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))
   pass_filter = (&(userPrincipalName=%u)(objectClass=person)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))

   # Home statique (fix %Ld/%Ln)
   user_attrs = =home=/var/vmail/sodecaf.local/%Ln/,=uid=vmail,=gid=vmail,=mail=maildir:~/Maildir/
   ```

3. Rechargez la configuration de Dovecot :
   ```bash
   systemctl reload dovecot
   ```

4. **Tests de liaison depuis iRedMail** :
   *Test LDAP:*
   ```bash
   ldapsearch -x -H ldap://172.16.0.1:389 -D "CN=iredmail,OU=Services,OU=Sodecaf,DC=sodecaf,DC=local" -w Rootsio2017 -b "DC=sodecaf,DC=local" "(sAMAccountName=udev)" mail userPrincipalName displayName
   ```
   *Doit retourner les informations de l'utilisateur "udev".*

   *Test Doveadm:*
   ```bash
   doveadm user udev@sodecaf.local
   ```
   *Doit retourner : uid 2000, gid 2000, et les bons dossiers maildir.*

---

## ✉️ 4. Configuration de Postfix

1. Créez un fichier permettant de vérifier les adresses valides sur l'AD :
   ```bash
   nano /etc/postfix/ad_virtual_mailbox_maps.cf
   ```
   *Contenu :*
   ```ini
   server_host = 172.16.0.1
   server_port = 389
   version = 3
   bind = yes
   bind_dn = CN=iredmail,OU=Services,OU=Sodecaf,DC=sodecaf,DC=local
   bind_pw = Rootsio2017
   search_base = DC=sodecaf,DC=local
   scope = sub
   query_filter = (&(objectClass=user)(|(userPrincipalName=%s)(mail=%s)))
   result_attribute = userPrincipalName
   ```

2. Éditez la configuration principale de Postfix :
   ```bash
   nano /etc/postfix/main.cf
   ```
   Trouvez ou ajoutez la directive `virtual_mailbox_maps` pour qu'elle corresponde à :
   ```ini
   virtual_mailbox_maps = ldap:/etc/postfix/ad_virtual_mailbox_maps.cf, hash:/etc/postfix/virtual
   ```

3. Rechargez la configuration et vérifiez :
   ```bash
   systemctl reload postfix
   ```
   **Test avec Postmap:**
   ```bash
   postmap -q udev@sodecaf.local ldap:/etc/postfix/ad_virtual_mailbox_maps.cf
   ```
   *Si tout va bien, la commande retournera `udev@sodecaf.local`.*

---

## 🌍 5. Configuration de Roundcube (Webmail)

1. Effectuez la sauvegarde :
   ```bash
   cp /opt/www/roundcubemail/config/config.inc.php /opt/www/roundcubemail/config/config.inc.php.bak
   ```

2. Éditez le fichier de configuration principal :
   ```bash
   nano /opt/www/roundcubemail/config/config.inc.php
   ```
   - **Activez l'autocomplétion** (trouvez et remplacez la ligne présente en fonction de cela) :
     ```php
     $config['autocomplete_addressbooks'] = array("sql", "ad_global_abook");
     ```
   - **Ajoutez tout ce bloc** à la toute fin du fichier :
     ```php
     $config['ldap_public']["ad_global_abook"] = array(
         'name' => 'Annuaire Sodecaf AD',
         'hosts' => array('172.16.0.1'),
         'port' => 389,
         'use_tls' => false,
         'network_timeout' => 10,
         'ldap_version' => '3',
         'user_specific' => false,
         'base_dn' => 'DC=sodecaf,DC=local',
         'bind_dn' => 'CN=iredmail,OU=Services,OU=Sodecaf,DC=sodecaf,DC=local',
         'bind_pass' => 'Rootsio2017',
         'writable' => false, // Lecture seule (pas d'écriture vers AD)
         'scope' => 'sub',
         'filter' => '(&(objectClass=user)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))', // Users actifs
         'search_fields' => array('mail', 'cn', 'sAMAccountName', 'displayName', 'sn', 'givenName'),
         'fieldmap' => array(
             'name' => 'cn',
             'displayname' => 'displayName',
             'surname' => 'sn',
             'firstname' => 'givenName',
             'email' => 'userPrincipalName', // Puisque mail absent
             'phone:work' => 'telephoneNumber',
             'street:work' => 'streetAddress',
         ),
         'sort' => 'displayName',
         'fuzzy_search' => true,
         'sizelimit' => 0,
         'timelimit' => 10,
         'referrals' => false, // Ignore les referrals AD
     );
     ```

Sauvegardez en quittant nano. Roundcube recharge automatiquement cette configuration PHP.

3. **Valider les modifications :**
   - Connectez-vous sur **`https://iredmail/mail/`**
   - Identifiez-vous avec **`udev@sodecaf.local`**
   - Rendez-vous sur la section **Contacts > Annuaire Sodecaf AD** et vérifiez que les utilisateurs s'affichent correctement.
   - Envoyez un e-mail au compte `uadmin` pour vérifier les flux.

---

## ⚙️ 6. L’interface iRedAdmin

Pour gérer les configurations administratives, connectez-vous sur :
> **Lien :** `https://172.16.0.8/iredadmin`
> **Compte :** `postmaster@sodecaf.local`

*NB : Comme l'annuaire est délégué à l'Active Directory, cette console est d'un intérêt limité, mais permet tout de même d'attribuer et gérer l'espace disque / quota associé à chaque boîte mail.*

---

## 📚 Annexe : Procotoles et Ports SMTP / POP / IMAP

Lorsqu'un client de messagerie (Thunderbird, Outlook, etc.) s'y connecte, il passera par les protocoles suivants :

| Port | Protocole | Service / Rôle dans la connexion |
|------|-----------|----------------------------------|
| **25** | SMTP | Trafic entrant vers Postfix pour les transferts entre serveurs |
| **80** / **443** | HTTP / HTTPS | Accès au Webmail ou Interfaces proxy d'administration |
| **110** | POP3 | Récupération des mails *(désuet)* |
| **143** | IMAP | Accès aux courriers électroniques en ligne avec synchronisation |
| **465** | SMTPS | Incoming mail to Postfix over TLS (Ancien Outlook) |
| **587** | SMTP | Mail submission over TLS (Protocole sortant recommandé) |
| **993** / **995**| IMAPS / POP3S | Protocoles chiffrés pour IMAP et POP | 

* **SMTP** : (Simple Mail Transfer Protocol) Envoie les messages.
* **POP** : (Post Office Protocol) Récupère les mails en local (pas ou peu de persistance serveur).
* **IMAP** : (Internet Message Access Protocol) Permet d'accéder au serveur directement sans téléchargement aveugle en synchronisant tous les terminaux.
