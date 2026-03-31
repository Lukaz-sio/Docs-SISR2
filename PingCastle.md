# Audit de l'Active Directory avec PingCastle

## 1. Introduction à l'audit de l'Active Directory
L'Active Directory (AD) est un annuaire d'entreprise stockant des informations sur les ressources informatiques (ordinateurs, utilisateurs, groupes, autorisations).

Son audit est crucial pour :
- Maintenir la sécurité et la conformité de l'environnement informatique.
- Détecter toute activité malveillante (tentatives de piratage, modifications non autorisées, création de comptes frauduleux).
- Surveiller les journaux et événements de sécurité.
- Identifier les risques et évaluer la conformité réglementaire.

## 2. Présentation de PingCastle
**PingCastle** est un logiciel français d'audit de sécurité, très reconnu dans le secteur de la cybersécurité. 
- **Licence** : L'outil est gratuit pour auditer son propre annuaire Active Directory. (Une licence est requise pour auditer l'annuaire d'un client lors d'une prestation).
- **Principe** : L'outil évalue le domaine AD sur divers critères et génère des rapports (HTML et XML) interactifs. Il attribue une note globale sur 100 : **Plus la note est élevée, plus le serveur AD est vulnérable.** La note correspond à la note maximale obtenue parmi les 4 critères évalués.

## 3. Installation et Utilisation

### Prérequis
- Un serveur Windows avec le rôle AD (ex: `SRV-WIN1`). Il est recommandé de travailler sur un clone du serveur en production pour des raisons de praticité et de sécurité.

### Démarche
1. **Téléchargement** : Rendez-vous sur [pingcastle.com/download](https://www.pingcastle.com/download/) pour télécharger l'outil directement sur le serveur.
2. **Installation et exécution** : Vous pouvez vous appuyer sur le tutoriel complet d'IT-Connect : [Comment auditer l'Active Directory avec PingCastle](https://www.it-connect.fr/comment-auditer-lactive-directory-avec-pingcastle/).
3. **Génération du rapport** : Une fois l'audit lancé, PingCastle génère deux fichiers (pour le domaine *sodecaf.local* par exemple) :
   - Un fichier HTML (`ad_hc_sodecaf.local.html`).
   - Un fichier XML (`ad_hc_sodecaf.local.xml`).
4. **Analyse** : Ouvrez le fichier HTML avec un navigateur web afin d'étudier les indicateurs.

## 4. Sécurisation de l'Active Directory
L'objectif de cette démarche est de repérer puis de corriger les failles afin d'abaisser la note globale du rapport **en dessous de 25 points (zone verte)**. 

Pour trouver des solutions aux vulnérabilités détectées, vous devez vous appuyer sur les préconisations de l'ANSSI : 
- 🔗 [Guide de sécurité Active Directory de l'ANSSI](https://www.cert.ssi.gouv.fr/uploads/guide-ad.html)

---

## 5. Rapport d'audit et remédiations (À compléter)
*Cette section est destinée à accueillir votre rapport de sécurisation détaillant les vulnérabilités trouvées par l'outil et les contre-mesures que vous avez mises en place (ou proposées) pour faire baisser le score.*

### Partie A : Audit général du serveur AD (PingCastle)
| Vulnérabilités | Contre-mesures | Points | Difficulté |
| :--- | :--- | :---: | :---: |
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |

### Partie B : Audit des mots de passe (Specops Password Auditor)
*Afin d'aller plus loin et d'auditer la robustesse des mots de passe qui sont un autre point faible de l'AD, vous pouvez procéder à une vérification des hachages ayant subi une fuite publique avec **Specops Password Auditor** ([lien de téléchargement](https://specopssoft.com/specops-password-auditor-update/)).*

| Vulnérabilités | Contre-mesures | Difficulté |
| :--- | :--- | :---: |
| | | |
| | | |
| | | |
| | | |
| | | |
