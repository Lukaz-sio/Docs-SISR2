Installation de HaProxy pour faire un reverse proxy :

Sur une debian 12, mettre une ip, changer son nom et mettre à jour la machine



Installer haproxy

```bash
# Mise en place du reverse proxy sur une VM Debian 12
apt install haproxy
mkdir /etc/haproxy/cert
cd /etc/haproxy/cert
openssl genrsa -out privateKey.pem 4096
openssl req -new -x509 -days 365 -key privateKey.pem -out cert.pem
# On fusionne ensuite le certificat et la clé privée dans un même fichier :
cat cert.pem privateKey.pem > sodecaf.pem
nano /etc/haproxy/haproxy.cfg
#-----------------------------------
frontend proxyguacamole
        bind 192.168.0.10:40443 ssl crt /etc/haproxy/cert/sodecaf.pem
        default_backend back_guacamole

frontend proxypublic
        bind 192.168.0.10:80
        http-request redirect scheme https unless { ssl_fc }
        default_backend back_guacamole

backend back_guacamole
        option httpclose
        option httpchk HEAD / HTTP/1.0
        server srv-guacamole 192.168.0.100:8080 check
#-----------------------------------
# Vérifier la configuration de Haproxy
haproxy -c -f /etc/haproxy/haproxy.cfg
```

Redémarrer le service haproxy et l'activer :

```bash
systemctl restart haproxy
systemctl enable haproxy
```

---

# Suppression du /guacamole en fin d'URL sur serveur Guacamole
cd /var/lib/tomcat9/webapps
systemctl stop tomcat9
rm guacamole/ -Rf
mv ROOT/ ROOT-ORIGINAL/
mv guacamole.war ROOT.war
systemctl start tomcat9

