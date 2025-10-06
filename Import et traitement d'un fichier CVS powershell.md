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


- Des répertoires sont créés pour chaque agence dans `C:`.
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


Importation d'utilisateurs à partir d'un fichier CSV :


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
}<#------------------------------------------------------------------
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
}<#------------------------------------------------------------------
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
}
```


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