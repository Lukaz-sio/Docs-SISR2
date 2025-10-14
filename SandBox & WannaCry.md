
# TP : Analyse de modifications système avec Windows Sandbox

**Attention : Ce TP est à but strictement pédagogique et d’analyse. Il est illégal et dangereux d’exécuter ou de diffuser des malwares en dehors d’un environnement isolé et contrôlé. Ne jamais reproduire ce TP sur une machine réelle ou connectée à un réseau.**

---

## Objectif

Ce TP montre comment configurer une machine virtuelle Windows 11 et utiliser Windows Sandbox pour observer les modifications système lors de l’exécution d’un programme inconnu, en utilisant des outils comme Regshot.

---

## Étapes principales

### 1. Création et configuration de la machine virtuelle

- Créer une VM Windows 11 **Pro** sur ESXi.
- Dans les paramètres avancés de la VM, ajouter :
  - `isolation.tools.paste.disable = FALSE`
  - `isolation.tools.setGUIOptions.enable = TRUE`
- Lancer la VM dans VMware Workstation et configurer :
  - 8GB de RAM
  - 2 processeurs, 2 cœurs
  - Activer les options de virtualisation :  
    - Virtualize Intel VT-x/EPT  
    - Virtualize CPU performance counters

---

### 2. Installation de Windows Sandbox

- Ouvrir PowerShell en administrateur et exécuter :
  ```powershell
  Enable-WindowsOptionalFeature -FeatureName "Containers-DisposableClientVM" -All -Online
  ```

---

### 3. Création du fichier de configuration Sandbox

- Créer un fichier texte avec le contenu suivant et le nommer `config1.wsb` :

  ```xml
  <Configuration>
    <Networking>Enable</Networking>
    <MappedFolders></MappedFolders>
    <MemoryInMB>4096</MemoryInMB>
    <VGpu>Enable</VGpu>
    <LogonCommand>
      <Command>powershell.exe -ExecutionPolicy Bypass -Command "Invoke-WebRequest 'https://www.7-zip.org/a/7z2501-x64.exe' -OutFile c:\Users\WDAGUtilityAccount\Downloads\7z2501-x64.exe"</Command>
      <Command>powershell -ExecutionPolicy Bypass -Command "Set-MpPreference -DisableRealtimeMonitoring $true"</Command>
      <Command>powershell.exe -ExecutionPolicy Bypass -Command "Invoke-WebRequest 'https://github.com/notepad-plus-plus/notepad-plus-plus/releases/download/v8.8.6/npp.8.8.6.Installer.x64.exe' -OutFile c:\Users\WDAGUtilityAccount\Downloads\npp.8.8.6.Installer.x64.exe"</Command>
      <Command>powershell.exe -ExecutionPolicy Bypass -Command "Invoke-WebRequest 'https://github.com/Seabreg/Regshot/blob/master/Regshot-x64-Unicode.exe' -OutFile c:\Users\WDAGUtilityAccount\Downloads\Regshot-x64-Unicode.exe"</Command>
    </LogonCommand>
  </Configuration>
  ```

- Double-cliquer sur `config1.wsb` pour lancer Windows Sandbox avec la configuration souhaitée :
  - Réseau activé
  - 4Go de RAM
  - Accélération graphique
  - Windows Defender désactivé
  - Téléchargement automatique de 7zip, Notepad++ et Regshot

---

### 4. Utilisation des outils dans la Sandbox

- Installer les trois applications téléchargées.
- Utiliser Regshot pour :
  - Prendre un premier snapshot de la base de registre (`avant.hive`)
  - Exécuter le programme à analyser (**WannaCry**)
  - Prendre un second snapshot (`après.hive`)
  - Comparer les deux snapshots pour observer les modifications système

---

### 5. Utilisation de samples WannaCry

- Télécharger sur theZoo (usage pédagogique en Sandbox/VM isolée) : malware/Binaries/Ransomware.WannaCry/Ransomware.WannaCry.zip​

- Ouvrir uniquement dans la Sandbox ; l’archive est protégée par mot de passe fourni par theZoo.

#### Qu'est ce que WannaCry fait sur le PC ?

- Chiffre des fichiers, modifie l’arrière‑plan, affiche une note de rançon et propose un « decryptor » local.​

- Supprime les shadow copies et installe des composants (dont Tor/local) pour la communication C2.​ 

### 6. Précautions et nettoyage

- **Désactiver toutes les interfaces réseau** avant d’exécuter un programme inconnu.
- À la fermeture de Windows Sandbox, toutes les données sont supprimées.
- Supprimer la machine virtuelle utilisée pour le TP après analyse.

---

## Remarques

- Ce TP est conçu pour l’analyse et la compréhension des modifications système dans un environnement isolé.
- Ne jamais exécuter de programme malveillant sur une machine réelle ou connectée à un réseau.
- Respecter la législation en vigueur et les règles de sécurité informatique.

---



