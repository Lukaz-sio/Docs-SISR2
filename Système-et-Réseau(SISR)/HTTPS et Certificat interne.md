# Création du CA et mise en place du protocole HTTPS sur Apache2

## 1. Objectif

Sécuriser l’accès à votre site web avec HTTPS en créant votre propre autorité de certification (CA) et en configurant Apache2 pour utiliser SSL/TLS.

---

## 2. Installation et configuration d'OpenSSL

- Vérifiez l’installation d’OpenSSL :
  ```bash
  sudo apt install openssl
  ```

- Modifiez `/etc/ssl/openssl.cnf` :  
**Modifiez 
 Remplacez :
 ```
 dir = ./demoCA 
 ```
 par :
 ```
 dir = /etc/ssl
 ```
 **Modifiez également le chemin du certificat CA :**
 Remplacez :
 ```
 certificate = $dir/cacert.pem
 ```
 par :
 ```
 certificate = $dir/certs/cacert.pem
 ```

- Créez l’arborescence nécessaire :
  ```bash
  sudo mkdir -p /etc/ssl/
  sudo touch /etc/ssl/index.txt
  echo "01" > /etc/ssl/serial
  ```
  **Créez aussi le dossier `newcerts` en même temps que `certs` et `private` :**
  ```bash
  mkdir /etc/ssl/sodecaf/private
  mkdir /etc/ssl/sodecaf/certs
  mkdir /etc/ssl/sodecaf/newcerts
  ```

---

## 3. Création du certificat de l’autorité de certification (CA)

**a. Générer la clé privée de la CA :**
Si un dossier spécifique dans `/etc/ssl` est utilisé, il faut alors créer les dossiers `private`, `certs` et `newcerts` dans le dossier `/etc/ssl/sodecaf` :
```bash
mkdir /etc/ssl/sodecaf/private
mkdir /etc/ssl/sodecaf/certs
mkdir /etc/ssl/sodecaf/newcerts
```
```bash
sudo openssl genrsa -des3 -out /etc/ssl/private/cakey.pem 4096
sudo chmod 400 /etc/ssl/private/cakey.pem
```

**b. Générer le certificat auto-signé de la CA :**

Générez le certificat auto-signé pour votre autorité de certification :

```bash
sudo openssl req -new -x509 -days 1825 -key /etc/ssl/private/cakey.pem -out /etc/ssl/certs/cacert.pem
```

Lors de l’exécution de cette commande, remplissez les champs comme suit :

| Champ                        | Valeur à saisir           |
|------------------------------|---------------------------|
| Country Name (2 letter code) | **FR**                    |
| State or Province Name       | **France**                |
| Locality Name                | **Montauban**             |
| Organization Name            | **Sodecaf**               |
| Organizational Unit Name     | *(laisser vide)*          |
| Common Name                  | **ca.sodecaf.local**      |
| Email Address                | **webmaster@sodecaf.local** |

> **Astuce :** Vous pouvez laisser le champ « Organizational Unit Name » vide en appuyant simplement sur Entrée.

Ce certificat auto-signé servira à authentifier et valider les certificats émis pour vos serveurs

---

## 4. Création du certificat du serveur web

**a. Générer la clé privée du serveur :**

 Modifiez `/etc/ssl/openssl.cnf` :  
 Remplacez la variable `dir = ./demoCA` par `dir = /etc/ssl`.
 **Modifiez également le chemin du certificat CA :**
 Remplacez :
 ```
 certificate = $dir/cacert.pem
 ```
 par :
 ```
 certificate = $dir/certs/cacert.pem
 ```

**b. Générer la demande de certificat (CSR) :**
```bash
sudo openssl req -new -key /etc/ssl/private/srvwebkey.pem -out /etc/ssl/srvwebcert_dem.pem
```
Lors de l’exécution de cette commande, remplissez les champs comme suit :

| Champ                        | Valeur à saisir                  |
|:-----------------------------|:---------------------------------|
| Country Name (2 letter code) | **FR**                           |
| State or Province Name       | **France**                       |
| Locality Name                | **Montauban**                    |
| Organization Name            | **Sodecaf**                      |
| Organizational Unit Name     | *(laisser vide)*                 |
| Common Name                  | **nom_de_la_machine.sodecaf.local** |
| Email Address                | **webmaster@sodecaf.local**      |

> **Astuce :** Le Common Name doit correspondre au nom DNS ou au nom de la machine du serveur. Vous pouvez laisser le champ « Organizational Unit Name » vide en appuyant simplement sur Entrée.

**c. Copier la demande de certificat sur la machine CA :**

Dans le dossier `certs/` :
```bash
scp srvwebcert_dem.pem etudiant@172.16.0.20:/home/etudiant/
```
- Tapez "yes" si demandé pour la fingerprint.
- Entrez le mot de passe du compte `etudiant`.
- Vérifiez la copie : `srvwebcert_dem.pem 100%`

**d. Signer le certificat avec la CA :**
```bash
sudo openssl ca -policy policy_anything -out /etc/ssl/certs/srvwebcert.pem -infiles /etc/ssl/srvwebcert_dem.pem
```
*Répondez "y" aux questions de confirmation.*

**e. Déplacement et changement de propriétaire du certificat de la machine CA au serveur web**

```bash
scp /etc/ssl/sodecaf/certs/srvwebcert.pem etudiant@172.16.0.10:/home/etudiant
```
Sur le serveur Web :
```bash
mv /home/etudiant/srvwebcert.pem /etc/ssl/certs/
chown root:root /etc/ssl/certs/srvwebcert.pem
```

---

## Bonus : création d'un certificat autosigné, directement sur le serveur web
```bash
openssl genrsa -out /etc/ssl/private/srvwebkey.pem 4096
openssl req -new -x509 -days 1825 -key /etc/ssl/private/srvwebkey.pem -out /etc/ssl/certs/srvwebcert.pem
```

## 5. Configuration d’Apache2 pour HTTPS

**a. Activez le module SSL :**
```bash
sudo a2enmod ssl
sudo systemctl restart apache2
```

**b. Modifiez le fichier de configuration du site :**
Dans `/etc/apache2/sites-available/000-default.conf` ou votre fichier de virtual host :

Remplacez :
```apache
<VirtualHost *:80>
```
par
```apache
<VirtualHost *:443>
    SSLEngine on
    SSLCertificateFile /etc/ssl/certs/srvwebcert.pem
    SSLCertificateKeyFile /etc/ssl/private/srvwebkey.pem
</VirtualHost>
```
- Activation du site et redémarrage du service Apache2
```bash
a2ensite sodecaf-ssl.conf
systemctl restart apache2
```

**c. Rediriger HTTP vers HTTPS :**
Activez le module rewrite :
```bash
sudo a2enmod rewrite
```
Ajoutez dans le virtual host port 80 :
```apache
<VirtualHost *:80>
    RewriteEngine On
    RewriteCond %{HTTPS} !=on
    RewriteRule ^/?(.*) https://%{SERVER_NAME}/$1 [R,L]
</VirtualHost>
```

---

## 6. Débogage et vérification

- Pour isoler les erreurs SSL :
  ```apache
  ErrorLog /var/log/apache2/error_ssl.log
  LogLevel debug
  ```
  Visualisez les logs :
  ```bash
  tail -f /var/log/apache2/error_ssl.log
  ```

- Testez la connexion SSL :
  ```bash
  openssl s_client -connect nom_dns:443
  ```

---

## 7. Test du serveur web sécurisé

- Accédez à votre site via https://IP_ou_DNS
- Ajoutez une exception dans le navigateur (alerte normale, CA inconnue).
- Vérifiez les infos du certificat et de l’autorité de certification.

---

## Ressources

- [Service web sécurisé - Réseau Certa](https://www.reseaucerta.org/content/service-web-securise)

---

Votre serveur web est maintenant accessible en HTTPS avec un certificat signé par votre propre autorité
