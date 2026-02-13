# Installation de Kali Linux sur VirtualBox

## 1. Télécharger l’image ISO de Kali Linux
- Rendez-vous sur le site officiel : [https://www.kali.org/get-kali/](https://www.kali.org/get-kali/)
- Téléchargez l’image ISO adaptée à votre architecture (généralement 64 bits).

## 2. Créer une nouvelle machine virtuelle dans VirtualBox
- Ouvrez VirtualBox et cliquez sur **Nouvelle**.
- Donnez un nom à la VM (ex : `Kali Linux`).
- Type : **Linux**
- Version : **Debian (64 bits)**

## 3. Configurer la machine virtuelle
- Attribuez au moins **2048 Mo de RAM** (4096 Mo recommandé).
- Dans l’onglet **Réseau**, choisissez **Accès par pont** et sélectionnez votre interface réseau.

## 4. Démarrer la machine virtuelle
- Lancez la VM.
- Sélectionnez l’ISO de Kali Linux téléchargée lors du premier démarrage.

## 5. Lancer l’installation graphique
- Dans le menu d’accueil, choisissez **Graphical install**.

## 6. Choisir les paramètres régionaux
- Langue : **Français**
- Zone géographique : **France**
- Clavier : **Français**

## 7. Définir le nom de la machine et du domaine
- Entrez le nom de votre machine.
- Domaine : laissez sur `home` si vous n’en avez pas.

## 8. Créer l’utilisateur et le mot de passe
- Saisissez le nom d’utilisateur souhaité.
- Choisissez un mot de passe sécurisé.

## 9. Partitionner le disque
- Choisissez **Assisté - utiliser un disque entier**.
- Sélectionnez le disque proposé par défaut.
- Choisissez **Tout dans une seule partition**.
- Terminez le partitionnement et appliquez les changements.

## 10. Confirmer l’écriture sur le disque
- Sélectionnez **Oui** pour appliquer les changements.
- L’installation du système commence.

## 11. Choisir les logiciels à installer
- Laissez la sélection par défaut des logiciels proposés.

## 12. Installer le programme de démarrage GRUB
- Choisissez **Oui** pour installer GRUB.
- Sélectionnez `/dev/sda` comme périphérique d’installation.

## 13. Fin de l’installation
- Sélectionnez **Continuer** pour redémarrer la machine.

## 14. Premier démarrage de Kali Linux
- Au redémarrage, choisissez **Kali Linux** dans le menu de démarrage.
- Connectez-vous avec l’utilisateur et le mot de passe créés.
- Bienvenue sur Kali