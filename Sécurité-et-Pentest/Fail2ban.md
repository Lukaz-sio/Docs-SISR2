# Installation et Configuration de Fail2Ban pour Sécuriser Apache2 sur Debian 12

## 1. Visualisation des logs Apache

Pour observer les requêtes reçues par le serveur :

```bash
tail -n 20 /var/log/apache2/access.log
```

## 2. Installation de Fail2Ban

Installez Fail2Ban :

```bash
sudo apt update
sudo apt install fail2ban
```

Si Fail2Ban ne démarre pas, modifiez `/etc/fail2ban/jail.conf` :

```ini
[sshd]
enabled = true
port = ssh
logpath = %(sshd_log)s
backend = systemd
```

## 3. Installation d’iptables (si nécessaire)

Fail2Ban utilise iptables pour bannir les IP :

```bash
sudo apt install iptables
```

## 4. Redémarrage et vérification du service Fail2Ban

```bash
sudo systemctl restart fail2ban
sudo systemctl status fail2ban
```

## 5. Configuration de la protection Apache contre les attaques DOS

### a. Modification du format des logs Apache

Éditez `/etc/apache2/apache2.conf` :

Commentez la ligne existante :

```apache
#LogFormat "%h %l %u %t \"%r\" %>s %O \"%{Referer}i\" \"%{User-Agent}i\"" combined
```

Ajoutez la nouvelle ligne :

```apache
LogFormat "%h %l %u %t %I %O \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\" %V %p" combined
```

Redémarrez Apache :

```bash
sudo systemctl restart apache2
```

### b. Création du fichier de configuration Fail2Ban pour Apache DOS

Créez `/etc/fail2ban/jail.d/apache-get-dos.conf` :

```ini
[apache-get-dos]
enabled = true
port = http,https
filter = apache-get-dos
logpath = /var/log/apache2/access.log
datepattern = %%d/%%b/%%Y:%%H:%%M:%%S %%z
maxretry = 300
findtime = 5m
bantime = 1h
```

### c. Définition des règles par défaut de bannissement

Créez `/etc/fail2ban/jail.d/custom.conf` :

```ini
[DEFAULT]
bantime = 300
findtime = 300
banaction = iptables-allports
```

### d. Création du filtre Fail2Ban pour Apache DOS

Créez `/etc/fail2ban/filter.d/apache-get-dos.conf` :

```ini
# Fail2Ban filter to scan Apache access.log for DoS attacks
[INCLUDES]
before = common.conf

[Definition]
failregex = ^<HOST> .*"GET (?!\/robots\.txt).*" (200|301|302|400|401|403|404|408|503)\s
ignoreregex =
```

### e. Redémarrage du service Fail2Ban

```bash
sudo systemctl restart fail2ban
```

## 6. Test de la protection contre les attaques DOS

Lancez une attaque de test avec slowhttptest :

```bash
slowhttptest -c 200 -H -g -o slowhttp -i 10 -r 200 -t GET -u http://172.16.0.10 -x 24 -p 80
```

## 7. Vérification des IP bannies

Pour vérifier le statut du filtre :

```bash
sudo fail2ban-client status apache-get-dos
```

Pour visualiser les IP bloquées par iptables :

```bash
sudo iptables -L
```

---

Fail2Ban est maintenant configuré pour protéger votre serveur Apache2 contre les attaques DOS sur Debian 12.
