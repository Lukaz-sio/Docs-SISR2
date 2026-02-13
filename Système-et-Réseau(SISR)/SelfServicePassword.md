# INSTALLATION SELF SERVICE PASSWORD (SSP) - DEBIAN 13 & SAMBA 4


# 1. Mise à jour et installation des dépendances PHP/Apache

```bash
sudo apt update && sudo apt install apache2 php php-ldap php-mbstring php-curl php-gd smarty4 -y
```

# 2. Correction de la compatibilité Smarty pour Debian 13

```bash
sudo mkdir -p /usr/share/php/smarty3
sudo ln -sf /usr/share/php/smarty4/Smarty.class.php /usr/share/php/smarty3/Smarty.class.php
```

# 3. Installation du paquet SSP (assurez-vous d'être dans le bon dossier)
# Remplacez le nom du fichier si votre version diffère

```bash
sudo apt install ./self-service-password_1.6.0-1_all.deb -y
```

# 4. Configuration de l'Alias Apache (/motdepasse au lieu de /ssp)

```bash
sudo sed -i 's/Alias \/ssp/Alias \/motdepasse/g' /etc/apache2/conf-available/self-service-password.conf
```

# 5. ACTIVATION de la configuration dans Apache

```bash
sudo a2enconf self-service-password
sudo systemctl restart apache2
```

# 6. Autorisation du certificat SSL (pour permettre le LDAPS)

```bash
echo "TLS_REQCERT allow" | sudo tee -a /etc/ldap/ldap.conf
sudo systemctl restart apache2
```

# 7. Rappel des paramètres à éditer manuellement dans :
# sudo nano /etc/self-service-password/config.inc.php

```ini
$ldap_url = "ldaps://localhost";
$ldap_binddn = "cn=Administrator,cn=Users,dc=greta,dc=lan";
$ldap_bindpw = "VOTRE_MOT_DE_PASSE";
$ldap_base = "dc=greta,dc=lan";
$pwd_mode = "ad";
$samba_mode = true;
$keyphrase = "UnePhraseTresLongueEtSecrete";
```

# 8. Attribution des droits finaux

```bash
sudo chown -R www-data:www-data /usr/share/self-service-password
sudo systemctl reload apache2
```
---

# DÉSINSTALLATION COMPLÈTE ET NETTOYAGE SSP

## 1. Suppression du paquet et des dépendances inutiles

```bash
sudo apt purge self-service-password -y
sudo apt autoremove -y
```

## 2. Suppression des fichiers de configuration Apache

```bash
sudo a2disconf self-service-password
sudo rm -f /etc/apache2/conf-available/self-service-password.conf
sudo rm -f /etc/apache2/sites-available/ssp.conf
```

## 3. Suppression des dossiers de l'application et des logs

```bash
sudo rm -rf /usr/share/self-service-password
sudo rm -rf /etc/self-service-password
sudo rm -rf /var/lib/self-service-password
```

## 4. Suppression du lien symbolique Smarty et du dossier créé

```bash
sudo rm -f /usr/share/php/smarty3/Smarty.class.php
sudo rmdir /usr/share/php/smarty3 2>/dev/null
```

## 5. Nettoyage de la configuration LDAP (SSL)
Note : Cette commande retire la dernière ligne du fichier ldap.conf

si c'était "TLS_REQCERT allow"

```bash
sudo sed -i '$d' /etc/ldap/ldap.conf
```

## 6. Redémarrage d'Apache pour valider le nettoyage

```bash
sudo systemctl restart apache2
echo "Nettoyage terminé. Le serveur est prêt pour une réinstallation propre."
```