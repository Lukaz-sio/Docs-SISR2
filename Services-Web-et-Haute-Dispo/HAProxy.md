# Documentation HAProxy

HAProxy est une solution de répartition de charge (load balancing) et de proxy inverse (reverse proxy) haute performance. Cette documentation couvre l'installation et la configuration de HAProxy dans deux environnements différents : sur une machine Debian et sur OPNSense.

## Table des matières
- [Prérequis](#prérequis)
- [Configuration des serveurs Web en mode actif/actif](#configuration-des-serveurs-web-en-mode-actifactif)
- [Installation sur Debian](#installation-sur-debian)
- [Configuration sur Debian](#configuration-sur-debian)
- [Configuration HTTPS](#configuration-https)
- [Installation sur OPNSense](#installation-sur-opnsense)

## Prérequis
- Deux serveurs Web configurés avec Apache2
- Une machine pour HAProxy (Debian ou OPNSense)
- Accès réseau aux serveurs Web

## Configuration des serveurs Web en mode actif/actif

Pour configurer les serveurs Web en mode actif/actif avec Apache2 démarré sur les deux serveurs :

```bash
crm resource stop serviceWeb
crn resource stop IPFailover
crm configure delete servweb
crm resource start IPFailover 
crn configure clone cServiceWeb serviceWeb
crm resource start serviceWeb
```

## Installation sur Debian

### 1. Mise à jour du système

```bash
apt update && apt upgrade -y
```

### 2. Installation des paquets nécessaires

```bash
apt install haproxy openssl -y
```

### 3. Configuration du nom d'hôte

```bash
# Modifier le fichier hosts
nano /etc/hosts  # Remplacer Debian par haproxy

# Modifier le nom d'hôte
nano /etc/hostname # Remplacer Debian par haproxy

# Redémarrer pour appliquer les changements
reboot
```

### 4. Configuration réseau

Dans VMware Workstation :
1. Créer un "LAN segment" nommé "DMZ Sodecaf"
2. Configurer les deux serveurs Web dans ce segment DMZ

## Configuration sur Debian

### Configuration de base

1. Ouvrir le fichier de configuration :
```bash
nano /etc/haproxy/haproxy.cfg
```

2. Configuration initiale simple :
```ini
listen httpProxy
        bind 172.16.0.13:80
        balance roundrobin
        option httpclose
        option httpchk HEAD / HTTP/1.0
        server srv-web1 192.168.0.1:80 check
        server srv-web2 192.168.0.2:80 check
        stats uri /statsHaproxy
        stats auth root:Rootsio2017
        stats refresh 30s
```

### Configuration avancée

Pour une meilleure lisibilité et maintenance, vous pouvez utiliser une configuration plus structurée :

```ini
frontend websodecaf
        bind 172.16.0.13:80
        default_backend clusterweb

backend clusterweb
        balance roundrobin
        option httpclose 
        option httpchk HEAD / HTTP/1.0
        server srv-web1 192.168.0.1:80 check
        server srv-web2 192.168.0.2:80 check
        stats uri /statsHaproxy
        stats auth root:Rootsio2017
        stats refresh 30s
```

### Répartition de charge personnalisée

Pour ajuster la répartition de charge entre les serveurs, utilisez le paramètre `weight` (valeurs de 1 à 255) :

```ini
server srv-web1 192.168.0.1:80 weight 100 check  # Reçoit 2/3 du trafic
server srv-web2 192.168.0.2:80 weight 50 check   # Reçoit 1/3 du trafic
```

### Test et monitoring

1. Tester l'accès au site web : `http://172.16.0.13`
2. Accéder aux statistiques HAProxy : `http://172.16.0.13/statsHaproxy`



## Configuration HTTPS

### 1. Création des certificats SSL

```bash
# Créer le répertoire pour les certificats
mkdir /etc/haproxy/cert
cd /etc/haproxy/cert

# Générer la clé privée
openssl genrsa -out /etc/haproxy/cert/privateKey.pem 4096

# Générer le certificat
openssl req -new -x509 -days 365 -key /etc/haproxy/cert/privateKey.pem -out /etc/haproxy/cert/cert.pem
```

Informations à fournir pour le certificat :
| Champ | Valeur |
|-------|---------|
| Country Name | FR |
| State | France |
| Locality | Montauban |
| Organization | Sodecaf |
| Organizational Unit | [laisser vide] |
| Common Name | www.sodecaf.local |
| Email Address | admin@sodecaf.local |

### 2. Fusion des certificats

```bash
cat cert.pem privateKey.pem > sodecaf.pem
```

### 3. Configuration HTTPS dans HAProxy

Modifier le fichier de configuration pour activer HTTPS et la redirection automatique :

```ini
frontend websodecaf
        bind 172.16.0.13:443 ssl crt /etc/haproxy/cert/sodecaf.pem
        default_backend clusterweb

frontend sodecafhttp
        bind 172.16.0.13:80
        http-request redirect scheme https unless { ssl_fc }
        default_backend clusterweb
```
## Installation sur OPNSense

### 1. Configuration réseau initiale

1. Configurer les interfaces réseau :
   - Interface 1 : Mode Bridge
   - Interface 2 : Mode Host-only
   - Interface 3 : LAN Segment (DMZ)

2. Vérifier la connexion réseau et mettre à jour OPNSense :
   - System → Firmware → Updates → Status → Check for updates
   - Installer toutes les mises à jour disponibles

3. Configurer l'interface DMZ :
   - Interfaces → Assignments
   - Assigner la nouvelle carte à la DMZ
   - Activer l'interface
   - Configurer l'IP : 192.168.0.254

### 2. Installation de HAProxy

1. Installer le plugin HAProxy :
   - System → Firmware → Plugins
   - Rechercher et installer `os-haproxy`

### 3. Configuration des serveurs

1. Configurer les serveurs backend :
   - Services → HAProxy → Settings → Real Servers
   - Créer SRV-WEB1 (192.168.0.1:80)
   - Créer SRV-WEB2 (192.168.0.2:80)
   - Appliquer les changements

### 4. Configuration SSL/TLS

1. Créer l'autorité de certification :
   - System → Trust → Authorities → Add
   - Method : Create an internal Certificate Authority
   - Description : CA SODECAF
   - Remplir les informations :
     - Country Code : France
     - State : France
     - City : Montauban
     - Organization : Sodecaf
     - Email : admin@sodecaf.local
     - Common Name : www.sodecaf.local

2. Créer le certificat serveur :
   - System → Certificates → Add
   - Method : Create an internal Certificate
   - Type : Server Certificate
   - Issuer : CA SODECAF

### 5. Configuration HAProxy

1. Configurer le backend pool :
   - Services → HAProxy → Virtual Services → Backend Pools
   - Nom : BACKEND WEB SODECAF
   - Ajouter les deux serveurs
   - Algorithm : Round Robin
   - Sauvegarder

2. Configurer le frontend :
   - Services → HAProxy → Virtual Services → Public Services
   - Nom : Frontend-web-https
   - Listen Address : [IP_OPNSENSE]:443
   - Type : SSL/HTTPS
   - Backend Pool : BACKEND WEB SODECAF
   - Enable SSL offloading : Oui
   - Certificates : [Certificat web sodecaf]

### 6. Configuration du pare-feu

1. Ajouter une règle entrante :
   - Firewall → Rules → WAN → Add
   - Protocol : TCP
   - Destination : WAN address
   - Destination port : HTTPS
   - Action : Allow

### 7. Activation du service

1. Activer HAProxy :
   - Services → HAProxy → Settings → Service
   - Enable HAProxy : Oui
   - Appliquer les changements

### 8. Test

Accéder au site web en utilisant l'IP de l'OPNSense : `https://[IP_OPNSENSE]`

