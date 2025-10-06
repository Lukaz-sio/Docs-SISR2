# Installation d'un DNS avec redondance sous Debian 12

Ce guide explique comment configurer un serveur DNS redondant sous Debian 12 en utilisant BIND9.

---

## Prérequis

- Deux machines Debian 12 (srv-dns1 et srv-dns2)
- Deux machines Debian 12 (srv-web1 et sev-web2)
- Réseau configuré (exemple : 172.16.0.0/24)

---

## Étape 1 : Préparation des serveurs

### 1.1 Modifier la configuration réseau et renommer les machines

Sur chaque machine, modifiez les fichiers `/etc/hosts` et `/etc/hostname` :

1. Ouvrez le fichier `/etc/hostname` et remplacez le contenu par `srv-dns1` dans la première machine et `srv-dns2` pour la seconde machine.
2. Ouvrez le fichier `/etc/hosts` et ajoutez les lignes suivantes :

   ```
   127.0.0.1   localhost
   127.0.1.1   srv-dns1
   ```

3. Redémarrez la machine pour appliquer les modifications :

   ```bash
   reboot
   ```

### 1.2 Installer BIND9

Sur chaque serveur :

```bash
apt update
apt install bind9
```

---

## Étape 2 : Configuration du serveur maître (srv-dns1)

### 2.1 Définir la zone DNS

Éditez `/etc/bind/named.conf.local` :

```bash
zone "sodecaf.fr" {
    type master;
    file "db.sodecaf.fr";
    allow-transfer {172.16.0.4;}; # IP du serveur esclave
};

zone "0.16.172.in-addr.arpa" {
    type master;
    file "db.172.16.0.rev";
    allow-transfer {172.16.0.4;};
};
```

### 2.2 Créer les fichiers de zone

Dans `/var/cache/bind/`, créez `db.sodecaf.fr` :

```bash
nano /var/cache/bind/db.sodecaf.fr
```

Contenu exemple :

```bash
$TTL 86400
@   IN  SOA srv-dns1.sodecaf.fr. hostmaster.sodecaf.fr. (
        2025092201 ; serial
        86400      ; refresh
        21600      ; retry
        3600000    ; expire
        3600 )     ; negative cache TTL
@       IN  NS  srv-dns1.sodecaf.fr.
@       IN  NS  srv-dns2.sodecaf.fr.

srv-dns1    IN  A   172.16.0.3
srv-dns2    IN  A   172.16.0.4
srv-web1    IN  A   172.16.0.10
srv-web2    IN  A   172.16.0.11
www         IN  A   172.16.0.12
web1        IN  CNAME srv-web1.sodecaf.fr.
web2        IN  CNAME srv-web2.sodecaf.fr.
```

Vérifiez la configuration avec :

```bash
named-checkzone sodecaf.fr /var/cache/bind/db.sodecaf.fr
```

### 2.3 Créer la zone inverse

Copiez le fichier de zone directe et modifiez-le :

```bash
cp /var/cache/bind/db.sodecaf.fr /var/cache/bind/db.172.16.0.rev
nano /var/cache/bind/db.172.16.0.rev
```

Gardez la partie SOA et NS, supprimer la partie en dessous puis ajoutez :

```bash
3   IN  PTR srv-dns1.sodecaf.fr.
4   IN  PTR srv-dns2.sodecaf.fr.
10  IN  PTR srv-web1.sodecaf.fr.
11  IN  PTR srv-web2.sodecaf.fr.
12  IN  PTR www.sodecaf.fr.
```

Vérifiez la configuration avec :

```bash
named-checkzone 0.16.172.in-addr-arpa /var/cache/bind/db.172.16.0.rev
```

---

## Étape 3 : Configuration du serveur esclave (srv-dns2)

### 3.1 Définir les zones esclaves

Dans `/etc/bind/named.conf.local` :

```bash
zone "sodecaf.fr" {
    type slave;
    file "slave/db.sodecaf.fr";
    masters {172.16.0.3;};
};

zone "0.16.172.in-addr.arpa" {
    type slave;
    file "slave/db.172.16.0.rev";
    masters {172.16.0.3;};
};
```

### 3.2 Préparer le dossier slave

```bash
mkdir /var/cache/bind/slave
chgrp bind /var/cache/bind/slave
chmod g+w /var/cache/bind/slave
```

---

## Étape 4 : Configuration des options globales

Sur les deux serveurs, éditez `/etc/bind/named.conf.options` :

- Décommentez et adaptez les forwarders pour l’accès Internet :

```bash
forwarders {
    8.8.8.8;
};
```

- Pour autoriser les requêtes de tous les réseaux :

```bash
allow-query { any; };
```

---

## Étape 5 : Redémarrage et vérification

Redémarrez BIND9 sur chaque serveur :

```bash
systemctl restart bind9
```

Vérifiez la configuration :

```bash
named-checkzone sodecaf.fr /var/cache/bind/db.sodecaf.fr
named-checkzone 0.16.172.in-addr-arpa /var/cache/bind/db.172.16.0.rev
```

Les deux commandes ci-dessus doivent renvoyer le numéro de série et "OK".

---

## Étape 6 : Tests

- Depuis Windows :

```powershell
nslookup web1.sodecaf.fr 172.16.0.3
nslookup srv-web2.sodecaf.fr 172.16.0.4
nslookup 172.16.0.10 172.16.0.3
```

- Depuis Linux :

```bash
dig web1.sodecaf.fr @172.16.0.3
dig -x 172.16.0.10 @172.16.0.3
```

---

## Étape 7 : Sécurisation du DNS avec DNSSEC

### 7.1 Activer DNSSEC dans les options

Modifiez le fichier `/etc/bind/named.conf.options` et changez la ligne suivante :

```bash
dnssec-validation auto
```

En :

```bash
dnssec-validation yes
```

### 7.2 Générer les clés DNSSEC

Créez un dossier pour stocker les clés :

```bash
cd /etc/bind/
mkdir keys
cd keys/
```

#### Générer les clés ZSK (Zone Signing Key)

```bash
dnssec-keygen -a rsasha1 -b 1024 -n zone sodecaf.fr
ls -l
```

Notez les clés générées :
- Clé publique : `Ksodecaf.fr.+005+09778.key`
- Clé privée : `Ksodecaf.fr.+005+09778.private`

#### Générer les clés KSK (Key Signing Key)

```bash
dnssec-keygen -a rsasha1 -b 1024 -f KSK -n zone sodecaf.fr
ls -l
```

Notez également ces clés.

### 7.3 Ajouter les clés dans le fichier de zone

Modifiez le fichier `/var/cache/bind/db.sodecaf.fr` et ajoutez les lignes suivantes :

```bash
; KSK
$include "/etc/bind/keys/Ksodecaf.fr.+005+48151.key"

; ZSK
$include "/etc/bind/keys/Ksodecaf.fr.+005+09778.key"
```

### 7.4 Signer la zone

Utilisez la commande suivante pour signer la zone :

```bash
dnssec-signzone -o sodecaf.fr -t -k /etc/bind/keys/Ksodecaf.fr.+005+48151 db.sodecaf.fr /etc/bind/keys/Ksodecaf.fr.+005+09778
```

### 7.5 Modifier la configuration pour utiliser la zone signée

Dans `/etc/bind/named.conf.local`, modifiez la ligne suivante :

```bash
file "db.sodecaf.fr";
```

En :

```bash
file "db.sodecaf.fr.signed";
```

### 7.6 Tester DNSSEC

Sur une machine cliente, exécutez la commande suivante :

```bash
dig +dnssec www.sodecaf.fr
```

Le résultat doit inclure une clé chiffrée, confirmant que DNSSEC est activé avec succès.

---

**Votre DNS est maintenant sécurisé avec DNSSEC !**