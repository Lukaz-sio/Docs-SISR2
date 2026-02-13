# Site Web PHP avec Base SQL

## 1. Se connecter à MySQL

```bash
mysql -u root -p
```

## 2. Afficher les bases de données

```sql
SHOW DATABASES;
```

## 3. Créer une base de données

```sql
CREATE DATABASE nom;
```

## 4. Créer un utilisateur avec mot de passe et droits

```sql
CREATE USER 'User'@'localhost' IDENTIFIED BY 'secret';
GRANT ALL PRIVILEGES ON nom.* TO 'User'@'localhost';
FLUSH PRIVILEGES;
```

## 5. Voir les utilisateurs existants

```sql
SELECT user, host FROM mysql.user;
```

## 6. Importer un fichier SQL

- Quittez MySQL :  
  ```sql
  exit
  ```
- Placez vos fichiers `.sql` dans `/home/etudiant`
- Importez le fichier :
  ```bash
  mysql nom < nom_du_fichier.sql
  ```

## 7. Utiliser la base de données

```sql
USE nom;
```

## 8. Afficher le contenu d'une table

```sql
SELECT * FROM Visiteur;
```

---

Adapte les noms (`nom`, `User`, `Visiteur`, etc.) selon ton projet.


