
# Scripts PowerShell Active Directory — Recueil et explications

Ce document rassemble tous les scripts PowerShell présents dans
`Import et traitement d'un fichier CVS powershell.md` et les présente
dans un seul fichier de documentation. Tous les scripts sont inclus
strictement tels qu'ils apparaissent dans le fichier source (non modifiés).
Chaque script est suivi d'une explication en français pour faciliter
la lecture et l'utilisation.

---

## Cheatsheet — commandes PowerShell importantes (à connaître)

Cette section liste les commandes et concepts PowerShell les plus utilisés
dans tes scripts, avec une courte explication et exemples d'usage.

### Commandes d'I/O et CSV

- Import-Csv / ipcsv : lit un fichier CSV et crée des objets PowerShell.
  Exemple : `Import-Csv "users.csv" -Delimiter ';'`.
- Export-Csv : exporte des objets PowerShell en CSV.
- Get-Content / Set-Content / Out-File : lecture/écriture de fichiers texte.

### Gestion de fichiers et dossiers

- Test-Path <chemin> : vérifie si un fichier ou dossier existe (renvoie booléen).
- New-Item -ItemType Directory -Path <chemin> : crée un dossier.
- Remove-Item <chemin> : supprime fichier/dossier (utiliser avec précaution).
- Get-ChildItem (alias dir / ls) : énumère les fichiers/dossiers.
- Out-Null : supprime la sortie console (utile pour éviter le bruit).

### Manipulation de chaînes

- .Substring(start,length) : extrait une portion d'une chaîne.
- .Length : longueur de la chaîne.
- .ToUpper() / .ToLower() : changer la casse.
- + (concaténation) : assemble des chaînes.

### Contrôle de flux

- ForEach-Object / foreach { } : itération sur une collection.
- If / Else : branchement conditionnel.
- switch(<expression>) { cas { } } : sélection multi-valeurs (très utilisé
  pour mapper des valeurs, ex : couleur selon fonction).
- try { } catch { } : gestion d'exceptions.

### Opérateurs usuels

- -eq, -ne, -lt, -gt : opérateurs de comparaison.
- -like, -notlike : correspondances par motif (wildcards `*`).
- -contains : recherche d'élément dans une collection.

### Cmdlets Active Directory (module ActiveDirectory)

- Import-Module ActiveDirectory : charge le module AD (nécessaire avant
  d'utiliser les cmdlets AD).
- New-ADOrganizationalUnit : crée une UO.
  Ex : `New-ADOrganizationalUnit -Name "Employés" -Path "dc=ex,dc=local"`.
- Get-ADOrganizationalUnit : recherche d'UO (supporte -Filter / -SearchBase).
- Remove-ADOrganizationalUnit -Recursive -Confirm:$false : suppression
  d'une UO avec enfants (utiliser avec extrême prudence).
- New-ADUser : création d'un compte AD (nombreux paramètres : -Name,
  -SamAccountName, -AccountPassword, -Path, -Enabled, -HomeDirectory...).
- Enable-ADAccount : active un compte AD nouvellement créé.
- New-ADGroup / Add-ADGroupMember : création de groupes et ajout de membres.
- Get-ADGroup / Get-ADUser : requêtes d'objets AD.

### Sécurité des mots de passe

- Read-Host -AsSecureString : saisie sécurisée d'un mot de passe depuis
  la console (ne s'affiche pas en clair).
- ConvertTo-SecureString <plain> -AsPlainText -Force : convertit une chaîne
  en SecureString (utilisé ici pour passer un mot de passe en clair à New-ADUser).
  Attention : stocker ou afficher des mots de passe en clair est dangereux.

### Génération aléatoire

- Get-Random : génère des valeurs pseudo-aléatoires (utile pour composer
  un mot de passe, choisir un caractère aléatoire, etc.).

### Commandes NTFS / permissions (module externe ex: NTFSSecurity)

- Set-NTFSOwner -Path <chemin> -Account <compte> : change le propriétaire NTFS.
- Add-NTFSAccess -Path <chemin> -Account <compte> -AccessRights FullControl :
  ajoute une entrée ACL (nécessite un module tiers comme `NTFSSecurity`).

### Raccourcis et bonnes pratiques d'exécution

- Utiliser `-WhatIf` et `-Confirm` quand disponibles pour simuler
  l'exécution d'une cmdlet destructrice.
- Exécuter PowerShell en tant qu'administrateur pour les opérations AD
  et sur le système de fichiers.
- Préférer l'usage de SecureString et de coffres pour stocker des secrets
  (LAPS, Azure Key Vault, HashiCorp Vault, etc.) au lieu de mots de passe
  en clair dans des scripts.

### Sortie et couleur

- Write-Host -ForegroundColor <Color> <texte> : affiche du texte coloré
  dans la console (utile pour la lisibilité des scripts d'import/traitement).

### Utilisation du pipeline

- Les cmdlets PowerShell sont conçues pour être chaînées via le pipeline `|`.
  Ex : `Import-Csv | ForEach-Object { ... }` permet de traiter chaque ligne
  du CSV comme un objet.

---

## Table des matières

- Présentation et prérequis
- Scripts : import CSV et création de dossiers
- Scripts : installation et import du module AD
- Scripts : création d'UO, groupes et comptes AD (diverses variantes)
- Scripts : génération de mots de passe
- Scripts : création de lecteurs réseaux et permissions NTFS
- Remarques de sécurité et bonnes pratiques

---

## Présentation et prérequis

- Exécuter PowerShell en tant qu'administrateur.
- Installer RSAT/les outils Active Directory si vous n'êtes pas sur un
  contrôleur de domaine.
- Charger le module ActiveDirectory : `Import-Module ActiveDirectory`.
- Pour les opérations NTFS présentées, installer le module `NTFSSecurity`
  ou un équivalent qui fournit `Set-NTFSOwner` et `Add-NTFSAccess`.

---

## Scripts : import CSV et création de dossiers (1)

Script original (strictement identique au fichier source) :

```powershell
<#-------------------------------------------------------------------
Import et traitement d'un fichier CSV
Auteur CLB – 29/09/2025
---------------------------------------------------------------------#>
ipcsv ".\utilisateurs sodecaf.csv" -Delimiter ";" | foreach { 
    $agence = $_.agency;
    if ((Test-Path ("c:\"+$agence)) -eq $false) {
        New-Item ("c:\"+$agence) -ItemType "Directory" | Out-Null
    }


    $couleur = switch($_.function) {
        comptable {"yellow"}
        accueil {"blue"}
        informatique {"cyan"}
        default {"white"}
    }


    $triGramme = $_.firstname.substring(0,1)+$_.lastname.substring(0,1)
    $triGramme = $triGramme + $_.lastname.substring($_.lastname.length-1,1)
    $trigramme = $triGramme.toUpper()


    if ((Test-Path ("c:\"+$agence+"\fic_"+$trigramme)) -eq $false) {
        New-Item ("c:\"+$agence+"\fic_"+$trigramme) -ItemType "Directory" 
    }
    else {
        write-Host ("Dossier utilisateur déjà existant")
    }


    Write-Host -ForegroundColor $couleur ($_.firstname+" "+$_.lastname+" ("+$triGramme+") "+$_.phone1)
}
```

Explication :

- `ipcsv` est utilisé comme abréviation de `Import-Csv` (selon l'environnement).
- Lit le fichier `utilisateurs sodecaf.csv` avec `;` comme séparateur.
- Pour chaque ligne :
  - récupère le champ `agency` pour créer un dossier `C:\<agency>` si
    il n'existe pas ;
  - calcule un trigramme à partir du prénom/nom ;
  - crée un sous-dossier `fic_<TRIGRAMME>` dans l'agence s'il n'existe pas ;
  - affiche le nom et téléphone en couleur selon la fonction (`function`).

Remarques :

- Les chemins sont locaux (`C:\...`) — adaptez si vous souhaitez un
  partage réseau.
- Vérifier que `ipcsv` est bien défini sur votre système ou remplacez par
  `Import-Csv` si nécessaire.

---

## Scripts : import CSV et affichage (2) — variante

Script original (strictement identique au fichier source) :

```powershell
<#-------------------------------------------------------------------
Apprentissage PowerShell - Script n° 4
Auteur CLB – 29/09/2025
Import et traitement d'un fichier csv
---------------------------------------------------------------------#>
ipcsv ".\utilisateurs sodecaf.csv" -Delimiter ";" | foreach { 
    $agence = $_.agency;
    if ((Test-Path ("c:\"+$agence)) -eq $false) {
        New-Item ("c:\"+$agence) -ItemType "Directory" | Out-Null
    }
    $couleur = switch($_.function) {
        comptable {"yellow"}
        accueil {"blue"}
        informatique {"cyan"}
        default {"white"}
    }
    $triGramme=$_.firstname.substring(0,1)+$_.lastname.substring(0,1)
    $triGramme = $triGramme + $_.lastname.substring($_.lastname.length-1,1)
    $trigramme = $triGramme.toUpper()




    Write-Host -ForegroundColor $couleur ($_.firstname+" "+$_.lastname+" ("+$triGramme+") "+$_.phone1)
    }
```

Explication :

- Variante très proche du script précédent — effectue la même logique
  d'import et d'affichage. Celle-ci ne crée pas explicitement les dossiers
  `fic_<trigramme>` (ce bloc montre surtout l'affichage coloré).

---

## Scripts : installation et import du module AD

Script original (strictement identique au fichier source) :

```powershell
Add-WindowsFeature RSAT-AD-PowerShell
```

Explication :

- Installe la fonctionnalité RSAT Active Directory PowerShell sur un
  serveur Windows (commande à exécuter sur un Windows Server).

Script original (strictement identique au fichier source) :

```powershell
Import-Module ActiveDirectory


New-ADOrganizationalUnit -Name "Employés" -Path "dc=sodecaf,dc=local" -ProtectedFromAccidentalDeletion $false


New-ADUser -Name "Paul Bismuth" -GivenName Paul -Surname Bismuth `
-SamAccountName pbismuth -UserPrincipalName pbismuth@supinfo.com `
-AccountPassword (Read-Host -AsSecureString "Mettez ici votre mot de passe") `
-Path "ou=Employés,dc=sodecaf,dc=local" `
-PassThru | Enable-ADAccount


New-ADGroup -name "Politique" -groupscope Global -Path "ou=Employés,dc=sodecaf,dc=local"


Add-ADGroupMember -Identity "Politique" -Members "pbismuth"
```

Explication :

- `Import-Module ActiveDirectory` : charge le module AD.
- `New-ADOrganizationalUnit` : crée l'UO `Employés` dans le domaine `sodecaf.local`.
- `New-ADUser` : exemple de création d'utilisateur `Paul Bismuth` ; la
  commande demande un mot de passe via `Read-Host -AsSecureString` ;
- `New-ADGroup` : création d'un groupe `Politique` ;
- `Add-ADGroupMember` : ajout de `pbismuth` au groupe.

---

## Scripts : suppression forcée d'une UO

Script original (strictement identique au fichier source) :

```powershell
Import-Module ActiveDirectory


Function effaceUO ($name) {
    if ((Get-ADOrganizationalUnit -filter "DistinguishedName -like 'ou=$name,dc=sodecaf,dc=local'")) {
        Remove-ADOrganizationalUnit -Identity "ou=$name,dc=sodecaf,dc=local" -Recursive -Confirm:$false
        Write-Host "UO $name a bien été supprimée"
    }
    else
    {
        Write-Host "UO $name n'existe pas"
    }
}
#--------------------------------------------------
effaceUO ("Employés")
```

Explication :

- Fonction utilitaire `effaceUO` qui supprime une UO si elle existe via
  `Remove-ADOrganizationalUnit -Recursive -Confirm:$false`. Utiliser avec
  une grande prudence — suppression non interactive.

---

## Scripts : Importation d'utilisateurs depuis CSV et création AD (TP5_scriptAD2.ps1)

Script original (strictement identique au fichier source) :

```powershell
<#------------------------------------------------------------------
Apprentissage PowerShell - TP5_scriptAD2.ps1
Fonction : Création de comptes AD à partir d'un fichier csv
Auteur CLB – 06/10/2025
--------------------------------------------------------------------#>


Import-Module ActiveDirectory
$ADUsers=Import-csv "C:\users\Administrateur\Documents\Powershell\utilisateurs sodecaf.csv" -Delimiter ";"


#-------- Fonction de génération de mot de passe --------------
Function CreatePassword() {


    for ($i=0;$i -lt 3;$i++){
        $min += Get-Random -InputObject a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z
    }


    for ($i=0;$i -lt 3;$i++){
        $maj += Get-Random -InputObject A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z
    }


    $nombre = Get-Random -Minimum 10 -Maximum 99


    $caracspec = Get-Random -InputObject !,?,$,*,_,+,=,:


    $pass = $min+$maj+$nombre+$caracspec


    return $pass
}


#-------- Parcours des utilisateurs dans le fichier csv --------------
foreach ($user in $ADUsers) {
    $prenom=$user.firstname
    $nom=$user.lastname
    $nom_complet=$prenom+" "+$nom
    $fonction=$user.Function
    $login=$prenom.Substring(0,1)+$nom
    $login=$login.tolower()
    $password=CreatePassword


echo ($prenom+" "+$nom+" "+$fonction+" "+$login+" "+$password)


#-------- Création des UO --------------
if ((Get-ADOrganizationalUnit -filter "DistinguishedName -like 'ou=Employés,dc=sodecaf,dc=local'") -eq $null) {
        New-ADOrganizationalUnit -Name "Employés" -Path "dc=sodecaf,dc=local" -ProtectedFromAccidentalDeletion $false
}
 
if ((Get-ADOrganizationalUnit -filter "DistinguishedName -like 'ou=$fonction,ou=Employés,dc=sodecaf,dc=local'") -eq $null) {
        New-ADOrganizationalUnit -Name $fonction -Path "ou=Employés,dc=sodecaf,dc=local" -ProtectedFromAccidentalDeletion $false
}


#-------- Création des groupes --------------
if ((Get-ADGroup -filter "DistinguishedName -like'CN=$fonction,ou=$fonction,ou=Employés,dc=sodecaf,dc=local'") -eq $null) {
    New-ADGroup -Name $fonction -GroupScope Global -GroupCategory Security -Path "ou=$fonction,ou=Employés,dc=sodecaf,dc=local"
}


#-------- Création des comptes et intégration dans un groupe --------------
try {
        New-ADUser -Name $nom_complet -GivenName $prenom -Surname $nom `
        -SamAccountName $login `
        -AccountPassword (ConvertTo-SecureString $password -AsPlainText -Force) `
        -Path "ou=$fonction,ou=Employés,dc=sodecaf,dc=local" `
        -Enabled $true


        Add-ADGroupMember -Identity $fonction -Members $login
    }
        catch {
        echo "L'utilisateur $login existe déjà"
    }
```

Explication :

- Importe le CSV en variable `$ADUsers`.
- `CreatePassword` génère un mot de passe combinant minuscules, majuscules,
  chiffres et caractère spécial.
- Pour chaque utilisateur :
  - calcule le login (1ère lettre du prénom + nom), le met en minuscule ;
  - crée les UO `Employés` puis `ou=<fonction>` si nécessaire ;
  - crée un groupe par fonction si nécessaire ;
  - crée l'utilisateur AD et l'ajoute au groupe ;
  - en cas de doublon, attrape l'exception et affiche un message.

---

## Scripts : (répétitions) — mêmes scripts TP5_scriptAD2.ps1 multiples

Le fichier source contient plusieurs copies identiques / très proches du
script `TP5_scriptAD2.ps1`. Pour rester fidèle au fichier d'origine,
les versions sont présentes dans le fichier source. Elles sont conceptuellement
les mêmes que le bloc précédent et servent à démontrer des variantes et
répétitions d'exécution.

> Note : les blocs répétitifs n'ont pas été modifiés et sont disponibles
> dans `Import et traitement d'un fichier CVS powershell.md` si vous
> souhaitez consulter chaque occurrence séparément.

---

## Scripts : création de comptes + lecteurs réseaux (TP5_scriptAD3.ps1)

Script original (strictement identique au fichier source) :

```powershell
<#------------------------------------------------------------------
Apprentissage PowerShell - TP5_scriptAD3.ps1
Fonction : Création de comptes AD à partir d'un fichier csv
            Ajout des lecteurs réseaux
Auteur CLB – 06/10/2025
--------------------------------------------------------------------#>


Import-Module ActiveDirectory
$ADUsers=Import-csv "c:\users\Administrateur\Desktop\script\utilisateurs sodecaf.csv" -Delimiter ";"
$dossier="c:\donnees\"


#-------- Fonction de génération de mot de passe --------------
Function CreatePassword() {


    for ($i=0;$i -lt 3;$i++){
        $min += Get-Random -InputObject a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z
    }


    for ($i=0;$i -lt 3;$i++){
        $maj += Get-Random -InputObject A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z
    }


    $nombre = Get-Random -Minimum 10 -Maximum 99


    $caracspec = Get-Random -InputObject !,?,$,*,_,+,=,:


    $pass = $min+$maj+$nombre+$caracspec


    return $pass
}


#-------- Parcours des utilisateurs dans le fichier csv --------------
foreach ($user in $ADUsers) {
    $prenom=$user.firstname
    $nom=$user.lastname
    $nom_complet=$prenom+" "+$nom
    $fonction=$user.Function
    $login=$prenom.Substring(0,1)+$nom
    $login=$login.tolower()
    $password="Btssio2017"


echo ($prenom+" "+$nom+" "+$fonction+" "+$login+" "+$password)


#-------- Création des UO --------------
if ((Get-ADOrganizationalUnit -filter "DistinguishedName -like 'ou=Employés,dc=sodecaf,dc=local'") -eq $null) {
        New-ADOrganizationalUnit -Name "Employés" -Path "dc=sodecaf,dc=local" -ProtectedFromAccidentalDeletion $false
}
 
if ((Get-ADOrganizationalUnit -filter "DistinguishedName -like 'ou=$fonction,ou=Employés,dc=sodecaf,dc=local'") -eq $null) {
        New-ADOrganizationalUnit -Name $fonction -Path "ou=Employés,dc=sodecaf,dc=local" -ProtectedFromAccidentalDeletion $false
}


#-------- Création des groupes --------------
if ((Get-ADGroup -filter "DistinguishedName -like'CN=$fonction,ou=$fonction,ou=Employés,dc=sodecaf,dc=local'") -eq $null) {
    New-ADGroup -Name $fonction -GroupScope Global -GroupCategory Security -Path "ou=$fonction,ou=Employés,dc=sodecaf,dc=local"
}


#-------- Création des comptes et intégration dans un groupe --------------
try {
        New-ADUser -Name $nom_complet -GivenName $prenom -Surname $nom `
        -SamAccountName $login `
        -AccountPassword (ConvertTo-SecureString $password -AsPlainText -Force) `
        -Path "ou=$fonction,ou=Employés,dc=sodecaf,dc=local" `
        -HomeDrive "U:" `
        -HomeDirectory "\172.16.0.1\donnees\$login" `
        -Enabled $true


        Add-ADGroupMember -Identity $fonction -Members $login
    }
    catch {
        echo "L'utilisateur $login existe déjà"
    }


#-------- Création du lecteur réseau par utilisateur --------------


    if (!(Test-Path ($dossier+$login))) {
        New-Item -Path $dossier -Name $login -ItemType "Directory"
        Set-NTFSOwner -Path ($dossier+$login) -Account "sodecaf.local\$login"
        Add-NTFSAccess -Path ($dossier+$login) -Account "sodecaf.local\$login" -AccessRights FullControl -AccessType Allow -PassThru
    }


}
```

Explication :

- Même logique d'import et de création AD, mais :
  - utilise un mot de passe par défaut `Btssio2017` ;
  - définit `HomeDrive` et `HomeDirectory` pour mapper un lecteur réseau ;
  - crée sur le serveur local (`c:\donnees\`) un dossier par utilisateur,
    définit le propriétaire NTFS et accorde FullControl (via `NTFSSecurity`).

Remarques :

- `Set-NTFSOwner` et `Add-NTFSAccess` proviennent d'un module externe
  (ex : `NTFSSecurity`). Assurez-vous qu'il est installé et importé avant
  d'exécuter ces commandes.

---

## Remarques de sécurité et bonnes pratiques

- Tester systématiquement dans un lab avant de déployer en production.
- Exécuter PowerShell avec les droits appropriés (compte admin AD).
- Éviter d'exposer des mots de passe en clair dans des logs et sorties.
  Préférer `ConvertTo-SecureString` et des coffres-forts pour les secrets.
- Faire des sauvegardes AD et prévoir une procédure de rollback pour
  les créations de masse.
- Utiliser `-WhatIf` et `-Confirm` lorsque disponible pour valider
  les conséquences d'une commande avant exécution réelle.

---

## Où trouver les scripts originaux

Tous les scripts inclus ici sont présents dans le fichier source :

`Import et traitement d'un fichier CVS powershell.md`

Consultez ce fichier pour voir les blocs d'origine dans leur contexte
initial.

---

Si vous voulez, je peux extraire chaque bloc de script en fichiers `.ps1`
séparés dans le dépôt (en laissant les fichiers markdown inchangés) et
ajouter un petit guide d'exécution avec exemples de commandes PowerShell
adaptées à Windows PowerShell (PowerShell v5.1) ou PowerShell Core.
