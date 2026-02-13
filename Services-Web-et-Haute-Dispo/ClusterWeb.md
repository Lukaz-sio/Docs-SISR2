# Mise en oeuvre d'un Cluster Web avec Corosync

Ce guide explique étape par étape comment installer et configurer un cluster web haute disponibilité avec Corosync, Pacemaker et crmsh.

---

## 1. Installation des paquets nécessaires

Installez Corosync, Pacemaker et crmsh sur chaque nœud du cluster :

```bash
apt install corosync pacemaker crmsh
```

---

## 2. Génération de la clé d'authentification

Générez la clé d'authentification pour Corosync :

```bash
corosync-keygen
```

Vérifiez la présence du fichier `authkey` :

```bash
ls /etc/corosync
```

Vous devez voir le fichier `authkey`.

---

## 3. Sauvegarde de la configuration

Avant toute modification, sauvegardez le fichier de configuration :

```bash
cp /etc/corosync/corosync.conf /etc/corosync/corosync.conf.save
```

---

## 4. Configuration du cluster

Modifiez le fichier `/etc/corosync/corosync.conf` pour définir les paramètres du cluster et les nœuds :

```ini
# /etc/corosync/corosync.conf

totem {
    version: 2
    cluster_name: cluster_web
    crypto_cipher: aes256
    crypto_hash: sha1
    clear_node_high_bit: yes
}

logging {
    fileline: off
    to_logfile: yes
    logfile: /var/log/corosync/corosync.log
    to_syslog: no
    debug: off
    timestamp: on
    logger_subsys {
        subsys: QUORUM
        debug: off
    }
}

quorum {
    provider: corosync_votequorum
    expected_votes: 2
    two_nodes: 1
}

nodelist {
    node {
        name: serv1   # À modifier selon le nom du serveur
        nodeid: 1
        ring0_addr: 172.16.0.10
    }
    node {
        name: serv2   # À modifier selon le nom du serveur
        nodeid: 2
        ring0_addr: 172.16.0.11
    }
}

service {
    ver: 0
    name: pacemaker
}
```

- Adaptez les noms (`serv1`, `serv2`) et les adresses IP à votre infrastructure.

---

## 5. Tester la configuration


Après avoir démarré Corosync, vérifiez la configuration du cluster et la détection des nœuds avec :

```bash
corosync-cfgtool -s
```

La commande `corosync-cfgtool -s` affiche l'état des nœuds. Vous verrez :

```
nodeid:         1:      localhost
nodeid:         2:      connected
```

---

## 6. Clonage du serveur web


**Pour assurer la haute disponibilité :**

- Éteignez le serveur web principal.
- Effectuez un clonage complet sur le second nœud.

**Pour vérifier que tout fonctionne :**

Utilisez la commande suivante :

```bash
crm status
crm configure show

```

La sortie doit indiquer que le cluster est **online** avec le nom des deux serveurs web, tels qu'ils sont définis dans `/etc/hosts` et dans `/etc/hostname` configuré précédemment.

---


### Désactiver le STONITH (Shoot The Other Node In The Head)

Pour désactiver le stonith :

```bash
crm configure property stonith-enabled=false
```

### Désactiver le Quorum

Pour ignorer la politique de quorum :

```bash
crm configure property no-quorum-policy="ignore"
```

### Modifier en cas d'erreur

Si des erreurs ont eté faites durant la configuration, il faut éditer le fichier `crm` :

```bash
crm configure edit
```


---

### Configuration du Failover IP

Pour configurer le failover d'IP :

```bash
crm configure primitive IPFailover ocf:heartbeat:IPaddr2 params ip=172.16.0.12 cidr_netmask=24 nic=ens33 iflabel=VIP
```

> **Remarque :** `ens33` correspond à l'interface réseau utilisée sur cet exemple. Pensez à remplacer `ens33` par le nom de votre propre interface réseau (ex : `eth0`, `enp0s3`, etc.) selon votre configuration.

Après configuration :
- La commande `ip a` affichera l'IP de la machine et l'IP du cluster.
- `crm configure show` permet de voir le nouveau paramètre.
- `crm status` affiche la ressource IPFailover.


---

### Tester le basculement du cluster

Pour mettre un nœud en standby :

```bash
crm node standby
```
> L'IP du cluster basculera automatiquement sur le nœud restant online.

Pour réactiver un nœud :

```bash
crm node online
```

---

### Créer une ressource pour le service web

Pour qu'un serveur gère le service web et l'autre le failover, créez la ressource :

```bash
crm configure primitive serviceWeb lsb:apache2 op monitor interval=60s op start interval=0 timeout=60s op stop interval=0 timeout=60s
```

---

### Regrouper les ressources IPFailOver et serviceWeb

Pour regrouper les deux ressources :

```bash
crm configure group servweb IPFailover serviceWeb meta migration-threshold="5"
```

---

### Définir une préférence de nœud primaire pour l'IP virtuelle

Pour déplacer la ressource IPFailOver sur un nœud spécifique :

```bash
crm resource move IPFailover srv-web1
```

---

Effacer une ressource :

```bash
crm resource cleanup
```


