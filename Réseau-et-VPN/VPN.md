# Établissons un VPN

## Contexte de travail

Devant l’augmentation des temps de télétravail, les développeurs de l’entreprise SODECAF souhaitent disposer de l’accès au réseau de l’entreprise et plus particulièrement aux fichiers du serveur web depuis leur domicile ou tout autre endroit connecté à internet. Vous devez leur configurer ce service en utilisant un VPN, permettant une authentification des utilisateurs et le chiffrement des échanges. La solution choisie est OpenVPN, protocole non standardisé – comprendre qu’il n’a pas fait l’objet d’une RFC – mais qui a l’avantage d’être libre. Il existe une version propriétaire qui inclut une interface graphique et quelques fonctionnalités supplémentaires.

Vous allez configurer un serveur OpenVPN sur le routeur pare-feu OPNsense et utiliser un client OpenVPN sur une machine
cliente (Windows ou Linux) en BTS-SIO.

---

## Table des matières
- [Prérequis](#prérequis)
- [Désactivation de HAProxy](#désactivation-de-haproxy)

## Prérequis
- Serveur Web configuré avec Apache2
- Windows Serveur avec AD + DHCP + DNS
- OPNsense

## Désactivation de HAProxy






L’interface web d’administration d’OPNsense est, par défaut, en écoute sur toutes les interfaces. Activez la uniquement
sur l’interface LAN, afin de laisser le port TCP 443 côté WAN disponible pour le VPN : menu Système > Paramètres >
Administration > Interfaces d’écoute.
· Configurez OPNsense en mettant en place :
▪ une autorité de certification CA-SODECAF : menu Système > Gestion des certificats > Autorités ;
▪ un certificat interne pour le serveur Sodecaf-VPN-Cert signé par l’autorité de certification CA-SODECAF : menu
Système > Gestion des certificats > Certificats ;
▪ un utilisateur de test du VPN : Flore Diaz : menu Système > Accès > Utilisateurs ;
▪ un certificat pour ce nouvel utilisateur : menu Système > Gestion des certificats > Certificats ;
▪ la configuration du serveur OpenVPN : menu VPN > OpenVPN > Instances :