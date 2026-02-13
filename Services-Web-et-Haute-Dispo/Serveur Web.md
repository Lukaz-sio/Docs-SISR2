# Installation et Configuration d’un Serveur Web Apache sur Debian 12

## 1. Installation d’Apache

Mettez à jour l’index des paquets et installez Apache :

```bash
sudo apt update
sudo apt install apache2
```

## 2. Vérification du Serveur Web

Vérifiez que le service Apache fonctionne :

```bash
sudo systemctl status apache2
```

Pour tester, récupérez l’adresse IP du serveur :

```bash
ip a
```

Accédez à cette adresse IP dans votre navigateur pour voir la page par défaut d’Apache.

## 3. Gestion du Service Apache

- **Arrêter Apache** :  
  `sudo systemctl stop apache2`
- **Démarrer Apache** :  
  `sudo systemctl start apache2`
- **Redémarrer Apache** :  
  `sudo systemctl restart apache2`
- **Recharger la configuration** :  
  `sudo systemctl reload apache2`
- **Désactiver le démarrage automatique** :  
  `sudo systemctl disable apache2`
- **Activer le démarrage automatique** :  
  `sudo systemctl enable apache2`

## 4. Configuration des Hôtes Virtuels

### a. Créer le répertoire du site

```bash
sudo mkdir -p /var/www/votre_domaine
sudo chown -R www-data:www-data /var/www/votre_domaine
sudo chmod -R 755 /var/www/votre_domaine
```

### b. Créer une page d’accueil

```bash
sudo nano /var/www/votre_domaine/index.html
```

Ajoutez :

```html
<html>
<head>
<title>Bienvenue !</title>
</head>
<body>
<h1>Succès ! L’hôte virtuel fonctionne !</h1>
</body>
</html>
```

### c. Créer le fichier de configuration de l’hôte virtuel

```bash
sudo nano /etc/apache2/sites-available/votre_domaine.conf
```

Ajoutez :

```apache
<VirtualHost *:80>
    ServerAdmin admin@votre_domaine
    ServerName votre_domaine
    ServerAlias www.votre_domaine
    DocumentRoot /var/www/votre_domaine
    DirectoryIndex index.html
    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```

### d. Activer le site et désactiver le site par défaut

```bash
sudo a2ensite votre_domaine.conf
sudo a2dissite 000-default.conf
```

### e. Vérifier la configuration

```bash
sudo apache2ctl configtest
```

Vous devriez voir : `Syntax OK`.

### f. Redémarrer Apache

```bash
sudo systemctl restart apache2
```

---

Votre serveur Apache sur Debian 12 est maintenant prêt à héberger votre site avec un hôte virtuel personnalisé