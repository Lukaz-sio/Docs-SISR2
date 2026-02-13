# DOCUMENTATION TECHNIQUE : SAMBA AD MULTI-MASTER (DC1 & DC2)
**Système :** Debian 13 (Trixie/Testing)
**Domaine :** domain.lan
**Royaume Kerberos :** DOMAIN.LAN

===========================================================================
## 1. ARCHITECTURE DES CONTRÔLEURS DE DOMAINE
===========================================================================
- DC1 (Primaire) : 192.168.1.10 | FQDN : samba1.domain.lan
- DC2 (Réplique)  : 192.168.1.11 | FQDN : samba2.domain.lan
===========================================================================



## 2. PRÉPARATION COMMUNE (À FAIRE SUR DC1 ET DC2)
# -------------------------------------------------------------------------

### A. Mise à jour du système
```bash
apt update && apt upgrade -y
```

### B. Configuration du nom d'hôte et des hosts
# Sur DC1 : hostnamectl set-hostname samba1
# Sur DC2 : hostnamectl set-hostname samba2
éditer `/etc/hosts` :

```bash
127.0.0.1       localhost
192.168.1.10    samba1.domain.lan  samba1
192.168.1.11    samba2.domain.lan  samba2
```

### C. Installation des paquets Samba AD

```bash
apt install -y acl attr samba samba-dsdb-modules samba-vfs-modules winbind \
libpam-winbind libnss-winbind krb5-config krb5-user dnsutils ntpdate
```

# Note : Lors du prompt Kerberos, entrer "GRETA.LAN" en MAJUSCULES.

## 3. CONFIGURATION DU PREMIER CONTRÔLEUR (DC1)
# -------------------------------------------------------------------------

### A. Provisioning du domaine
# On supprime la configuration SMB par défaut pour créer le domaine

```bash
rm /etc/samba/smb.conf
```

```bash
samba-tool domain provision \
  --realm=DOMAIN.LAN \
  --domain=DOMAIN \
  --server-role=dc \
  --dns-backend=SAMBA_INTERNAL \
  --adminpass='TonMotDePasseComplex123!' \
  --use-rfc2307
```

### B. Configuration Kerberos

```bash
cp /var/lib/samba/private/krb5.conf /etc/krb5.conf
```

### C. Gestion des services
# On désactive les services classiques pour activer le mode AD-DC

```bash
systemctl disable --now smbd nmbd winbind
systemctl unmask samba-ad-dc
systemctl enable --now samba-ad-dc
```

## 4. RÉPLICATION SUR LE SECOND CONTRÔLEUR (DC2)
# -------------------------------------------------------------------------

### A. Alignement DNS
# DC2 doit pointer sur DC1 pour trouver le domaine à rejoindre

```bash
echo "nameserver 192.168.1.10" > /etc/resolv.conf
```

### B. Jointure du domaine pour réplication
# On supprime la conf par défaut sur DC2

```bash
rm /etc/samba/smb.conf
```

# Commande de jointure en tant que DC supplémentaire

```bash
samba-tool domain join domain.lan DC -U"Administrator" --realm=DOMAIN.LAN
```

### C. Activation du service AD-DC sur DC2

```bash
cp /var/lib/samba/private/krb5.conf /etc/krb5.conf
systemctl disable --now smbd nmbd winbind
systemctl unmask samba-ad-dc
systemctl enable --now samba-ad-dc
```

## 5. VÉRIFICATIONS ET TESTS DE SANTÉ
# -------------------------------------------------------------------------

### A. Test de la réplication (à faire sur les deux)
# Affiche l'état des partenaires de réplication (Inbound/Outbound)

```bash
samba-tool drs showrepl
```

### B. Test des enregistrements DNS SRV
# Vérifie que les services AD sont bien publiés

```bash
host -t SRV _ldap._tcp.domain.lan
host -t SRV _kerberos._udp.domain.lan
```

### C. Vérification de l'authentification Kerberos
# Doit retourner un ticket sans demander de mot de passe si déjà logué

```bash
kinit Administrator
klist
```

### D. Test de synchronisation des objets
# Créer un utilisateur sur DC1, vérifier sa présence immédiate sur DC2
# Sur DC1 :

```bash
samba-tool user create testuser 'Password123!'
```

# Sur DC2 :

```bash
samba-tool user list | grep testuser
```

## 6. SÉCURITÉ ET PORTS (FIREWALL DEBIAN/STORMSHIELD)
# -------------------------------------------------------------------------
# Ports à ouvrir pour l'administration RSAT et la réplication :
# TCP : 135, 139, 445, 1024-65535 (RPC dynamique)
# TCP/UDP : 53 (DNS), 88 (Kerberos), 389 (LDAP), 464 (Kpasswd), 636 (LDAPS)
# UDP : 123 (NTP), 137-138 (NetBIOS)