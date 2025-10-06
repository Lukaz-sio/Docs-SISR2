# Import et traitement d'un fichier CSV avec PowerShell

## Présentation

Ce document explique comment utiliser PowerShell pour lire, traiter et organiser les données d'un fichier CSV. Les scripts présentés permettent de :

1. Lire et afficher les données d'un fichier CSV avec des filtres et des couleurs.
2. Créer des répertoires pour chaque agence et des sous-dossiers pour chaque utilisateur, basés sur un trigramme unique.

---

## Lecture et traitement d'un fichier CSV

### Code PowerShell

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

### Explication du code

1. **Lecture du fichier CSV** :
   - La commande `ipcsv` (abréviation de `Import-Csv`) lit le fichier `utilisateurs sodecaf.csv`.
   - Le délimiteur utilisé est `;`.

2. **Création des répertoires d'agence** :
   - La variable `$agence` récupère le nom de l'agence pour chaque utilisateur.
   - Si le répertoire de l'agence n'existe pas, il est créé avec `New-Item`.

3. **Définition des couleurs** :
   - La fonction de l'utilisateur (`function`) détermine la couleur d'affichage :
     - Cyan pour l'informatique.
     - Jaune pour les comptables.
     - Bleu pour l'accueil.
     - Blanc par défaut.

4. **Génération du trigramme** :
   - Le trigramme est constitué de :
     - La première lettre du prénom.
     - La première lettre du nom.
     - La dernière lettre du nom.
   - Le trigramme est converti en majuscules avec `ToUpper()`.

5. **Création des sous-dossiers utilisateurs** :
   - Chaque utilisateur a un dossier nommé `fic_<trigramme>` dans le répertoire de son agence.
   - Si le dossier existe déjà, un message est affiché.

6. **Affichage des informations** :
   - Le prénom, le nom, le trigramme et le téléphone sont affichés avec une couleur correspondant à la fonction de l'utilisateur.

---

## Résultat attendu

- Des répertoires sont créés pour chaque agence dans `C:\`.
- Chaque utilisateur a un sous-dossier nommé `fic_<trigramme>` dans le répertoire de son agence.
- Les informations des utilisateurs sont affichées dans la console avec des couleurs spécifiques selon leur fonction.

---

**Exemple d'affichage dans la console :**

- Informatique : `Cyan`
- Comptable : `Jaune`
- Accueil : `Bleu`
- Autres : `Blanc`



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


Installation du module ad sous powershell : 

```powershell
Add-WindowsFeature RSAT-AD-PowerShell
```

quand l'on veut utiliser l'active directory dans powershell il faut activer le module avec :

```powershell
Import-Module ActiveDirectory
```

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


Comment supprimer une UO de force :

Dans utilisateurs et ordinateurs Active Directory -> Affichage -> Fonctionnalités avancées -> clic droit sur l'UO -> Propriétés -> Objet -> décocher Protéger l'objet des suppresions accidentelles Puis clic droit sur l'uo et supprimer

pour nettoyer en ligne de commande powershell : 

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
