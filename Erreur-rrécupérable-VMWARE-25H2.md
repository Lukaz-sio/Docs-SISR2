# Réparer l'erreur irrécupérable SVGA

Ajouter la ligne suivante dans le fichier `.vmx` de la machine virtuelle : 

```ini
 mks.enableVulkanPresentation=FALSE
```

 Cela corrige un problème d'accélération 3D avec la nouvelle version de VMWare