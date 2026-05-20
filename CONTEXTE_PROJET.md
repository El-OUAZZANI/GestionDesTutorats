# CONTEXTE DU PROJET — Plateforme Django de Gestion des Tutorats

## 1. Présentation générale du projet

Ce projet est une application web développée avec Django.  
Le nom du projet est une plateforme de gestion des tutorats entre étudiants.

L’objectif principal est de permettre aux étudiants de chercher des tuteurs, réserver des séances de tutorat, consulter leurs sessions, gérer leurs demandes, et communiquer avec les autres utilisateurs.  
Le système contient aussi un espace tuteur et un espace administrateur.

La plateforme doit être moderne, simple à utiliser, claire et adaptée à un projet de fin d’année / PFA.

## 2. Technologies utilisées

Le projet utilise principalement :

- Python
- Django
- HTML
- CSS
- JavaScript
- Base de données relationnelle, probablement SQLite ou MySQL/MariaDB selon la configuration
- Templates Django
- Architecture Django classique : models, views, urls, templates, static files

Codex doit analyser le dossier Django ouvert dans VS Code pour confirmer la structure réelle du projet avant de proposer des modifications.

## 3. Objectif fonctionnel du site web

Le site web doit gérer trois espaces principaux :

1. Espace étudiant
2. Espace tuteur
3. Espace administrateur

Chaque espace possède ses propres pages, fonctionnalités et interfaces.

## 4. Acteurs du système

### Étudiant

L’étudiant est l’utilisateur principal de la plateforme.

Il peut :

- Créer un compte
- Se connecter
- Accéder à son dashboard étudiant
- Rechercher des tuteurs
- Consulter les matières disponibles
- Réserver une séance de tutorat
- Consulter ses sessions planifiées
- Voir l’état de ses demandes
- Envoyer ou recevoir des messages
- Consulter ses notifications
- Modifier son profil
- Activer le mode tuteur si nécessaire

### Tuteur

Le tuteur est aussi un utilisateur, mais avec des fonctionnalités supplémentaires.

Il peut :

- Activer le mode tuteur
- Accéder à un dashboard tuteur
- Gérer ses disponibilités
- Ajouter des créneaux horaires
- Modifier ou supprimer ses disponibilités
- Consulter les demandes de tutorat reçues
- Accepter ou refuser une demande
- Consulter les sessions à tutorer
- Gérer les matières enseignées
- Organiser son calendrier
- Communiquer avec les étudiants
- Consulter ses notifications

### Administrateur

L’administrateur gère la plateforme.

Il peut :

- Accéder au dashboard administrateur
- Gérer les comptes utilisateurs
- Consulter la liste des étudiants et tuteurs
- Activer, désactiver ou supprimer des utilisateurs
- Gérer les matières disponibles
- Ajouter, modifier ou supprimer une matière
- Suivre toutes les sessions de tutorat
- Consulter les statistiques du tableau de bord
- Contrôler les demandes et les données importantes de la plateforme

## 5. Fonctionnalités principales

### Authentification

Le système doit permettre :

- L’inscription d’un utilisateur
- La connexion
- La déconnexion
- La redirection selon le rôle
- La protection des pages par authentification

Après connexion, l’utilisateur doit être redirigé vers son espace adapté :

- Étudiant → dashboard étudiant
- Tuteur → dashboard tuteur ou mode tuteur
- Administrateur → dashboard admin

### Dashboard étudiant

Le dashboard étudiant doit afficher une vue générale de son activité.

Il peut contenir :

- Nombre de sessions réservées
- Prochaines séances
- Demandes en attente
- Notifications récentes
- Accès rapide à la recherche de tuteurs
- Accès rapide aux sessions
- Accès au profil

### Recherche de tuteurs

L’étudiant doit pouvoir rechercher un tuteur selon :

- La matière
- Le nom
- Le niveau
- La disponibilité
- Le mode de séance : en ligne ou présentiel

La page doit afficher les tuteurs sous forme de cartes modernes.

Chaque carte peut contenir :

- Nom du tuteur
- Matières enseignées
- Niveau
- Disponibilités
- Bouton pour consulter ou réserver

### Réservation de séance

L’étudiant peut réserver un créneau disponible chez un tuteur.

Le processus logique est :

1. L’étudiant choisit un tuteur
2. Il choisit une matière
3. Il choisit un créneau disponible
4. Il envoie une demande
5. La demande devient en attente
6. Le tuteur peut accepter ou refuser
7. Si le tuteur accepte, la session devient confirmée

Les statuts possibles d’une session peuvent être :

- pending / en attente
- confirmed / confirmée
- cancelled / annulée
- completed / terminée
- refused / refusée

### Gestion des disponibilités du tuteur

Le tuteur peut ajouter ses créneaux.

Chaque disponibilité peut contenir :

- Date
- Heure de début
- Heure de fin
- Matière concernée
- Mode : en ligne ou présentiel
- Salle ou lien de réunion
- Statut disponible ou réservé

### Sessions

Le système doit gérer les séances entre un tuteur et un étudiant.

Une session peut contenir :

- Tuteur
- Étudiant
- Matière
- Date et heure
- Statut
- Lieu ou lien
- Message de demande
- Date de création

### Matières enseignées

Le tuteur peut gérer les matières qu’il enseigne.

Il peut :

- Ajouter une matière
- Supprimer une matière
- Indiquer son niveau
- Ajouter une description

Exemples de matières :

- Python
- Java
- Django
- Mathématiques
- Base de données
- Algorithmique
- Réseaux
- Programmation web

### Messagerie

Le système peut contenir une messagerie interne.

Elle permet :

- À un étudiant d’envoyer un message à un tuteur
- À un tuteur de répondre
- De lier un message à une session
- De marquer les messages comme lus ou non lus

### Notifications

Le système peut générer des notifications.

Exemples :

- Nouvelle demande de tutorat
- Demande acceptée
- Demande refusée
- Nouveau message reçu
- Session confirmée
- Session annulée

### Administration

L’espace admin doit permettre une gestion globale.

Fonctionnalités attendues :

- Dashboard avec statistiques
- Nombre total d’utilisateurs
- Nombre total de tuteurs
- Nombre total d’étudiants
- Nombre de sessions
- Nombre de matières
- Liste des utilisateurs
- Gestion des matières
- Suivi des sessions
- Contrôle des demandes

## 6. Modèles importants attendus

Codex doit vérifier les modèles existants dans le dossier Django, mais voici la conception logique attendue.

### User

Représente un utilisateur.

Champs possibles :

- id
- username ou email
- password
- role
- is_active
- is_staff
- date_joined

### Profile

Complète les informations du compte utilisateur.

Champs possibles :

- user
- first_name
- last_name
- department
- study_year
- bio
- phone
- tutor_mode
- profile_image

Relation :

- Un User possède un Profile

### Subject

Représente une matière.

Champs possibles :

- name
- description
- created_at

### UserSubject

Relie un utilisateur à une matière.

Rôle :

- Permet de savoir quelles matières un tuteur enseigne
- Permet aussi de savoir quelles matières un étudiant recherche

Champs possibles :

- user
- subject
- relation_type : tutor ou tutee
- level
- description

### Availability

Représente un créneau disponible du tuteur.

Champs possibles :

- tutor
- subject
- date
- start_time
- end_time
- mode
- room
- is_available
- is_recurring

### Session

Représente une séance de tutorat.

Champs possibles :

- tutor
- student
- subject
- availability
- start_datetime
- end_datetime
- status
- location
- request_message
- created_at

### Message

Représente un message entre utilisateurs.

Champs possibles :

- sender
- receiver
- session
- content
- timestamp
- is_read

### Notification

Représente une notification.

Champs possibles :

- user
- type
- content
- is_read
- created_at

## 7. Pages principales attendues

### Pages générales

- Page d’accueil
- Page de connexion
- Page d’inscription
- Page de profil
- Page de déconnexion

### Pages étudiant

- Dashboard étudiant
- Recherche de tuteurs
- Détail d’un tuteur
- Réservation d’une séance
- Mes sessions
- Messages
- Notifications
- Profil étudiant

### Pages tuteur

- Dashboard tuteur
- Mes disponibilités
- Ajouter une disponibilité
- Sessions à tutorer
- Demandes reçues
- Matières enseignées
- Calendrier
- Messages
- Notifications
- Profil tuteur

### Pages administrateur

- Dashboard admin
- Gestion des utilisateurs
- Gestion des matières
- Gestion des sessions
- Statistiques
- Détail utilisateur
- Détail session

## 8. Design souhaité

Le design doit être :

- Moderne
- Clair
- Professionnel
- Style dashboard
- Couleurs principales : blanc, bleu moderne, bleu ciel, gris clair
- Cartes blanches avec ombres douces
- Sidebar moderne
- Boutons bleus
- Icônes simples
- Interface propre et académique
- Beaucoup d’espace
- Typographie moderne comme Inter, Poppins ou Montserrat

Les interfaces doivent être cohérentes entre :

- Étudiant
- Tuteur
- Administrateur

## 9. Structure visuelle souhaitée

Chaque dashboard doit idéalement contenir :

- Sidebar à gauche
- Header en haut
- Titre de la page
- Cartes statistiques
- Tableaux modernes
- Boutons d’action
- Messages de succès/erreur Django
- Contenu responsive

## 10. Règles importantes pour Codex

Avant de modifier le projet, Codex doit :

1. Lire la structure complète du dossier Django ouvert dans VS Code
2. Identifier les apps existantes
3. Identifier les fichiers importants :
   - settings.py
   - urls.py
   - models.py
   - views.py
   - forms.py
   - templates
   - static
4. Comprendre les routes existantes
5. Ne pas créer des fichiers inutiles si des fichiers existent déjà
6. Respecter la structure actuelle du projet
7. Proposer les changements avant modification
8. Donner les fichiers exacts à modifier
9. Garder un code simple, propre et compatible avec Django
10. Ne pas casser les pages déjà fonctionnelles

## 11. Autorisation donnée à Codex

Tu as l’autorisation de lire tous les fichiers du dossier Django actuellement ouvert dans VS Code.

Tu peux analyser :

- Les modèles
- Les vues
- Les URLs
- Les templates HTML
- Les fichiers CSS
- Les fichiers JavaScript
- Les formulaires
- Les fichiers de configuration

Tu peux proposer des modifications, mais avant de modifier un fichier, explique-moi :

- Quel fichier tu vas modifier
- Pourquoi tu vas le modifier
- Quelle fonctionnalité sera ajoutée ou corrigée

Ne modifie pas les fichiers sensibles sans me demander confirmation, notamment :

- settings.py
- fichiers .env
- base de données
- fichiers contenant des mots de passe ou clés secrètes

## 12. Objectif demandé à Codex

Analyse ce projet Django et aide-moi à :

- Corriger les erreurs
- Compléter les fonctionnalités manquantes
- Améliorer les dashboards
- Créer les interfaces étudiant, tuteur et administrateur
- Connecter les pages aux modèles Django
- Corriger les routes
- Améliorer le CSS
- Rendre le site plus moderne
- Préparer le projet pour un rapport PFA
- Garder une structure propre et professionnelle

## 13. Priorités du projet

Les priorités sont :

1. Authentification fonctionnelle
2. Dashboard étudiant
3. Mode tuteur
4. Dashboard tuteur
5. Gestion des disponibilités
6. Réservation des séances
7. Gestion des sessions
8. Matières enseignées
9. Interface administrateur
10. Design moderne et cohérent

## 14. Instruction finale pour Codex

Commence par analyser le projet sans modifier les fichiers.

Ensuite, donne-moi :

1. La structure du projet trouvée
2. Les apps Django détectées
3. Les modèles existants
4. Les vues existantes
5. Les routes existantes
6. Les templates existants
7. Les fonctionnalités déjà présentes
8. Les fonctionnalités manquantes
9. Un plan clair des prochaines modifications

Après cette analyse, attends mon accord avant de modifier les fichiers.