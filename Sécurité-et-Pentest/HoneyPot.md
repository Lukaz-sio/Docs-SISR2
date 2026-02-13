# Installation d'un Cowrie Honeypot (Debian 13)

Ce document décrit, pas à pas, l'installation et la configuration de Cowrie — un honeypot SSH/Telnet — sur une machine Debian 13.

## Pré-requis

- Accès root ou un compte avec sudo.
- Système à jour :

```bash
sudo apt update && sudo apt upgrade -y
```

- Paquets système recommandés :

```bash
sudo apt-get install -y git python3-pip python3-venv libssl-dev libffi-dev \
  build-essential libpython3-dev python3-minimal authbind iptables
```

Note : `authbind` est utile si vous souhaitez que Cowrie écoute directement sur des ports < 1024 sans droits root.

## Étapes d'installation

1. Créer un compte système non privilégié pour Cowrie et basculer sur ce compte :

```bash
sudo adduser --disabled-password cowrie
sudo su - cowrie
```

1. Récupérer le code source et se placer dans le répertoire :

```bash
git clone https://github.com/cowrie/cowrie
cd cowrie
```

1. Créer et activer un environnement virtuel Python, puis installer les dépendances :

```bash
python3 -m venv cowrie-env
source cowrie-env/bin/activate
python -m pip install --upgrade pip
python -m pip install --upgrade -r requirements.txt
python -m pip install -e .
```

1. Copier le fichier de configuration exemple et modifier si nécessaire :

```bash
cd etc
cp cowrie.cfg.dist cowrie.cfg
# Modifier cowrie.cfg selon vos besoins (ports, bannissements, logging, etc.)
```

Par défaut, Cowrie écoute sur le port 2222 pour SSH. Vous pouvez modifier ceci dans `etc/cowrie.cfg`.

## Redirection du port SSH (optionnelle)

Si vous voulez que toute connexion vers le port SSH standard (22) soit redirigée vers Cowrie (2222), utilisez iptables.

AVERTISSEMENT : Avant d'appliquer la redirection, assurez-vous que votre serveur SSH légitime n'est pas sur le port 22 (ou que vous avez un autre moyen d'accès), sinon vous risquez de vous couper l'accès.

Exemple : rediriger 22 vers 2222

```bash
# Installer iptables si nécessaire en root
su -
sudo apt install -y iptables
# Redirection du port 22 vers 2222
sudo iptables -t nat -A PREROUTING -p tcp --dport 22 -j REDIRECT --to-port 2222
sudo iptables-save
```

## Démarrer Cowrie

Revenir au compte `cowrie` (si vous êtes root) et démarrer le service :

```bash
su - cowrie
cd ~/cowrie
cowrie start
cowrie status
```

## Tester le honeypot

Depuis une machine de test (par ex. Kali) :

- Scanner les ports :

```bash
nmap -sV <IP>
# ex: nmap -sV 192.168.1.25
```

- Tenter une connexion SSH vers le port 2222 :

```bash
ssh -p 2222 root@<IP>
```

Cowrie est conçu pour simuler un environnement complet : connectez-vous avec un mot de passe aléatoire si besoin. L'environnement est virtuel et ne contient pas de données réelles.

## Logs et journalisation

Les logs de Cowrie se trouvent par défaut dans le répertoire `var/log/cowrie/` (ou selon la configuration). Surveillez `cowrie.log` et `tty/` pour les sessions capturées.

## Sécurité et recommandations

- Ne pas exécuter Cowrie en tant que root.
- Séparer l'accès SSH légitime et le honeypot (changer le port SSH réel).
- Surveiller régulièrement les logs et mettre en place des sauvegardes des logs si nécessaire.
- Si le honeypot reçoit beaucoup d'attaques, envisagez d'isoler la VM/réseau pour éviter tout impact sur l'infrastructure.

## Référence

- Référence : [Dépôt officiel Cowrie](https://github.com/cowrie/cowrie)

---
