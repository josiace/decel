# Guide de l'Espace Admin - DECEL

## 📋 Table des Matières

1. [Introduction](#introduction)
2. [Accès à l'Admin](#accès-à-ladmin)
3. [Vue d'Ensemble des Modèles](#vue-densemble-des-modèles)
4. [Gestion des Utilisateurs](#gestion-des-utilisateurs)
5. [Gestion des Examens](#gestion-des-examens)
6. [Gestion de l'Apprentissage](#gestion-de-lapprentissage)
7. [Gestion des Compétences](#gestion-des-compétences)
8. [Gestion de la Gamification](#gestion-de-la-gamification)
9. [Gestion des Recommandations](#gestion-des-recommandations)
10. [Gestion de la Communauté](#gestion-de-la-communauté)
11. [Bonnes Pratiques](#bonnes-pratiques)

---

## Introduction

L'espace admin de DECEL est l'interface de gestion qui permet aux administrateurs de contrôler tous les aspects de la plateforme d'apprentissage adaptatif. C'est ici que vous pouvez :

- Créer et gérer les comptes utilisateurs
- Configurer les examens et les questions
- Publier des cours et des TD
- Suivre les progrès des utilisateurs
- Modérer le contenu communautaire
- Configurer les badges et les règles de gamification

---

## Accès à l'Admin

### 1. Créer un Superutilisateur

Si ce n'est pas déjà fait, créez un compte administrateur :

```bash
python manage.py createsuperuser
```

Suivez les instructions pour définir :
- Un nom d'utilisateur
- Une adresse email
- Un mot de passe

### 2. Se Connecter

1. Démarrez le serveur : `python manage.py runserver`
2. Ouvrez votre navigateur sur : `http://localhost:2222/admin/`
3. Connectez-vous avec vos identifiants de superutilisateur

---

## Vue d'Ensemble des Modèles

L'admin Django est organisé par applications. Voici la structure :

### 📁 **ACCOUNTS** - Gestion des Utilisateurs
- **User** : Modèle d'utilisateur personnalisé avec XP, niveau, solde DC, bio, avatar
- **DCTransaction** : Historique des transactions DC (gains, dépenses, récompenses)
- **Contributor** : Gestion des contributeurs (créateurs de contenu)
- **Country** : Liste des pays disponibles

### 📁 **SKILLS** - Gestion des Compétences
- **Subject** : Matières (Mathématiques, Physique, etc.)
- **UserSkill** : Compétences des utilisateurs par matière

### 📁 **EXAMS** - Gestion des Examens
- **Exam** : Examens avec configuration de difficulté et temps limite
- **Question** : Questions d'examen
- **Choice** : Choix de réponse pour les questions QCM
- **ExamSession** : Sessions d'examen des utilisateurs
- **UserAnswer** : Réponses des utilisateurs aux questions

### 📁 **LEARNING** - Gestion de l'Apprentissage
- **Course** : Cours publiés
- **TD** : Travaux Dirigés
- **CorrectedTD** : Corrections de TD
- **CourseProgress** : Progression des utilisateurs dans les cours
- **TDProgress** : Progression des utilisateurs dans les TD

### 📁 **GAMIFICATION** - Gestion de la Gamification
- **XPLog** : Journal des gains d'XP
- **Badge** : Badges à débloquer
- **UserBadge** : Badges obtenus par les utilisateurs
- **Leaderboard** : Classements sociaux
- **LeaderboardEntry** : Entrées de classement

### 📁 **RECOMMENDATIONS** - Gestion des Recommandations
- **Recommendation** : Suggestions d'apprentissage générées automatiquement

### 📁 **COMMUNITY** - Gestion de la Communauté
- **Content** : Contenu soumis par la communauté
- **ModerationRule** : Règles de modération

---

## Gestion des Utilisateurs

### 📌 User (Comptes Utilisateurs)

**Champs principaux :**
- **Username** : Nom d'utilisateur unique
- **Email** : Adresse email
- **First Name** : Prénom
- **Last Name** : Nom
- **Total XP** : Points d'expérience cumulés
- **Level** : Niveau actuel (calculé automatiquement)
- **DC Balance** : Solde en Decelcone (DC) - monnaie pour les achats
- **Bio** : Biographie de l'utilisateur
- **Avatar** : Photo de profil
- **Is Staff** : Cocher pour donner accès à l'admin
- **Is Superuser** : Cocher pour tous les droits
- **Is Active** : Cocher pour activer le compte

**Actions disponibles :**
- **Filtres** : Par niveau, XP, statut actif
- **Recherche** : Par nom d'utilisateur ou email
- **Modification** : Changer les informations utilisateur
- **Suppression** : Supprimer un compte utilisateur

**⚠️ Important :**
- Ne modifiez pas manuellement le XP ou le niveau - ils sont calculés automatiquement
- Le solde DC peut être ajusté manuellement si nécessaire (avec prudence)
- Utilisez "Is Staff" pour donner accès à l'admin sans tous les droits

---

### 📌 DCTransaction (Transactions DC)

**Affichage et monitoring :**
- Enregistre toutes les transactions DC (gains, dépenses, récompenses)
- Champs :
  - **User** : Utilisateur concerné
  - **Transaction Type** : Type (purchase, sale, exam_reward, daily_bonus, referral, admin_grant, admin_deduct)
  - **Amount** : Montant (positif pour gain, négatif pour dépense)
  - **Balance After** : Solde DC après la transaction
  - **Description** : Description de la transaction
  - **Related Content Type** : Type de contenu lié (course, td, etc.)
  - **Related Content ID** : ID du contenu lié
  - **Created At** : Date de la transaction

**Types de transactions :**
- **purchase** : Achat de contenu par l'utilisateur
- **sale** : Vente de contenu par le créateur (75% commission)
- **exam_reward** : Récompense pour examen réussi (+5 DC)
- **daily_bonus** : Bonus quotidien de connexion (+5 DC + streak)
- **referral** : Bonus de parrainage (à implémenter)
- **admin_grant** : Octroi manuel de DC par l'admin
- **admin_deduct** : Déduction manuelle de DC par l'admin

**Utilisation :**
- Consultez l'historique des transactions DC
- Identifiez les patterns de gain/dépense
- Ajustez manuellement les soldes si nécessaire (avec prudence)
- Analysez l'activité économique de la plateforme

**⚠️ Important :**
- Les transactions sont créées automatiquement par le système
- Évitez de modifier manuellement les transactions existantes
- Utilisez les transactions admin_grant/admin_deduct pour les ajustements manuels

---

## Gestion des Examens

### 📌 Subject (Matières)

**Champs :**
- **Name** : Nom de la matière (ex: "Mathématiques")
- **Description** : Description de la matière

**Utilisation :**
- Créez d'abord les matières avant de créer des examens
- Les matières sont utilisées pour suivre les compétences par domaine

### 📌 Exam (Examens)

**Champs principaux :**
- **Title** : Titre de l'examen
- **Description** : Description détaillée
- **Subject** : Matière associée (obligatoire)
- **Difficulty** : Niveau de difficulté (1-5)
- **Time Limit** : Limite de temps en minutes (optionnel)
- **Passing Score** : Score minimum pour réussir (%)
- **Question Count** : Nombre de questions (calculé automatiquement)
- **Is Active** : Cocher pour rendre l'examen disponible

**Workflow de création d'un examen :**

1. **Créer l'examen**
   - Allez dans EXAMS → Exam → Ajouter
   - Remplissez les informations de base
   - Sélectionnez la matière
   - Définissez la difficulté et le score de passage
   - Sauvegardez

2. **Ajouter des questions**
   - Après sauvegarde, vous verrez "Questions" en bas
   - Cliquez sur "Ajouter une autre Question"
   - Pour chaque question :
     - **Text** : Énoncé de la question
     - **Order** : Ordre d'affichage
     - **Is Active** : Cocher pour activer

3. **Ajouter des choix de réponse**
   - Dans chaque question, cliquez sur "Ajouter un autre Choice"
   - Pour chaque choix :
     - **Text** : Texte de la réponse
     - **Is Correct** : ⚠️ **IMPORTANT** - Cocher SEULEMENT pour les bonnes réponses
     - **Order** : Ordre d'affichage

**⚠️ Règles critiques pour les examens :**
- Chaque question doit avoir AU MOINS UNE réponse correcte
- Le système utilise un QCM STRICT : l'utilisateur doit sélectionner TOUTES les bonnes réponses et AUCUNE mauvaise réponse pour que la question soit correcte
- Pas de crédit partiel

### 📌 ExamSession (Sessions d'Examen)

**Affichage uniquement :**
- Ces enregistrements sont créés automatiquement quand les utilisateurs passent des examens
- Vous pouvez consulter :
  - Le score obtenu
  - Si l'examen a été réussi
  - La date de passage
  - Les réponses détaillées

**Utilisation :**
- Consultez ces données pour analyser les performances
- Identifiez les examens trop difficiles ou trop faciles

### 📌 Question & Choice

**Gestion :**
- Utilisez les interfaces inline dans Exam pour gérer questions et choix
- Peut être modifié directement depuis la page de l'examen

---

## Gestion de l'Apprentissage

### 📌 Course (Cours)

**Champs principaux :**
- **Title** : Titre du cours
- **Description** : Description courte
- **Content** : Contenu du cours (supporte HTML)
- **Subject** : Matière associée
- **Author** : Auteur du cours
- **Is Published** : Cocher pour publier le cours

**Workflow :**
1. Créez d'abord la matière dans Skills → Subject
2. Créez un utilisateur auteur (ou utilisez votre compte)
3. Allez dans Learning → Course → Ajouter
4. Remplissez les informations
5. Utilisez HTML pour formater le contenu si nécessaire
6. Cochez "Is Published" pour rendre visible

**Conseils :**
- Utilisez des titres clairs et descriptifs
- Structurez le contenu avec des paragraphes
- Ajoutez des exemples et des exercices

### 📌 TD (Travaux Dirigés)

**Champs principaux :**
- **Title** : Titre du TD
- **Description** : Description
- **Content** : Énoncé des exercices
- **Subject** : Matière associée
- **Author** : Auteur
- **Is Published** : Cocher pour publier

**Workflow :**
Similaire aux cours, mais pour les exercices pratiques

### 📌 CorrectedTD (Corrections de TD)

**Champs principaux :**
- **TD** : TD associé (obligatoire)
- **Correction** : Solution détaillée des exercices
- **Author** : Auteur de la correction

**Workflow :**
1. Créez d'abord un TD
2. Allez dans Learning → CorrectedTD → Ajouter
3. Sélectionnez le TD
4. Rédigez la correction détaillée
5. Sauvegardez

**Conseils :**
- Expliquez chaque étape de la résolution
- Incluez des méthodes alternatives si possible
- Mettez en évidence les points clés

### 📌 CourseProgress & TDProgress

**Affichage uniquement :**
- Créés automatiquement quand les utilisateurs complètent des cours/TD
- Montrent :
  - Si le contenu est terminé
  - La date de complétion
  - Le score (pour les TD)

**Utilisation :**
- Analysez l'engagement des utilisateurs
- Identifiez les contenus populaires ou difficiles

---

## Gestion des Compétences

### 📌 Subject (Matières)

**Voir section Examens pour plus de détails**

### 📌 UserSkill (Compétences Utilisateur)

**Affichage et monitoring :**
- Ces enregistrements sont créés automatiquement
- Montrent pour chaque utilisateur et matière :
  - **Skill Percentage** : Pourcentage de compétence (0-100%)
  - **Total Exams Taken** : Nombre d'examens passés
  - **Total TD Completed** : Nombre de TD terminés
  - **Total Courses Read** : Nombre de cours lus
  - **Last Activity** : Dernière activité dans cette matière

**Calcul automatique :**
- Le pourcentage est calculé avec pondération temporelle
- Les activités récentes ont plus de poids
- Mis à jour automatiquement après chaque action

**Utilisation :**
- Identifiez les domaines forts et faibles des utilisateurs
- Adaptez les recommandations en fonction des compétences
- Suivez la progression globale

---

## Gestion de la Gamification

### 📌 XPLog (Journal des XP)

**Affichage uniquement :**
- Enregistre chaque gain d'XP
- Champs :
  - **User** : Utilisateur concerné
  - **Amount** : Quantité d'XP gagnée
  - **Reason** : Raison du gain (ex: "Examen terminé : Mathématiques")
  - **Action Type** : Type d'action (exam, td, course)
  - **Created At** : Date du gain

**Valeurs d'XP par défaut :**
- Examen réussi : 100 XP
- Examen échoué : 50 XP
- TD complété : 40 XP
- Cours lu : 20 XP

**Utilisation :**
- Audit de l'activité des utilisateurs
- Analyse des patterns d'engagement
- Détection d'activités anormales

### 📌 Badge (Badges)

**Champs principaux :**
- **Name** : Nom du badge
- **Description** : Description du badge
- **XP Threshold** : XP minimum requis
- **Exams Threshold** : Nombre d'examens minimum
- **Skill Threshold** : Pourcentage de compétence minimum
- **Icon** : Emoji ou nom d'icône

**Exemples de badges :**
- **Débutant** : 0 XP
- **Apprenti** : 500 XP
- **Étudiant** : 1000 XP, 5 examens
- **Expert** : 5000 XP, 20 examens, 70% compétence
- **Maître** : 10000 XP, 50 examens, 90% compétence

**Workflow de création :**
1. Allez dans Gamification → Badge → Ajouter
2. Définissez le nom et la description
3. Configurez les seuils (un ou plusieurs)
4. Ajoutez un emoji comme icône
5. Sauvegardez

**⚠️ Important :**
- Les badges sont attribués automatiquement quand les seuils sont atteints
- Configurez des seuils progressifs pour encourager la progression

### 📌 UserBadge (Badges Utilisateur)

**Affichage uniquement :**
- Créés automatiquement quand les utilisateurs atteignent les seuils
- Montrent :
  - L'utilisateur
  - Le badge obtenu
  - La date d'obtention

**Utilisation :**
- Consultez les badges obtenus par les utilisateurs
- Analysez les achievements populaires

---

## Gestion des Recommandations

### 📌 Recommendation (Recommandations)

**Affichage et monitoring :**
- Générées automatiquement par le système
- Champs :
  - **User** : Utilisateur concerné
  - **Recommendation Type** : Type (review, advance, practice, learn)
  - **Title** : Titre de la recommandation
  - **Description** : Description détaillée
  - **Context** : Données contextuelles (JSON)
  - **Priority** : Priorité (1-10)
  - **Is Active** : Si la recommandation est active
  - **Is Dismissed** : Si l'utilisateur a ignoré la recommandation

**Types de recommandations :**
- **Review** : Réviser une matière faible (priorité 9)
- **Practice** : Pratiquer avec des TD (priorité 7)
- **Advance** : Avancer dans une matière forte (priorité 6)
- **Learn** : Apprendre une nouvelle matière (priorité 5)

**Utilisation :**
- Consultez les recommandations générées
- Identifiez les patterns dans les suggestions
- Désactivez les recommandations obsolètes (Is Active = False)

**⚠️ Important :**
- Ne créez pas manuellement de recommandations
- Le système les génère automatiquement basé sur les performances

---

## Gestion de la Communauté

### 📌 Content (Contenu Communautaire)

**Champs principaux :**
- **Title** : Titre du contenu
- **Content Type** : Type (Course, TD, CorrectedTD)
- **Subject** : Matière associée
- **Description** : Description courte
- **Content** : Contenu principal
- **Author** : Auteur
- **Status** : Statut (draft, pending, approved, rejected)
- **Moderation Notes** : Notes du modérateur
- **Moderated By** : Modérateur
- **Moderated At** : Date de modération
- **Moderation Rule** : Règle appliquée

**Workflow de modération :**

1. **Contenu soumis** (status = pending)
   - Les utilisateurs soumettent du contenu
   - Il apparaît dans la file d'attente

2. **Modération** via l'interface web ou l'admin
   - Allez dans Community → Content
   - Filtrez par "pending"
   - Ouvrez le contenu à modérer
   - Changez le statut :
     - **Approved** : Approuver et publier
     - **Rejected** : Rejeter
   - Ajoutez des notes de modération
   - Sélectionnez une règle si applicable

3. **Publication** (status = approved)
   - Le contenu est visible par tous les utilisateurs

**Actions dans l'admin :**
- **Approuver** : Changez le statut en "approved"
- **Rejeter** : Changez le statut en "rejected"
- **Modifier** : Corrigez le contenu avant publication
- **Supprimer** : Supprimez définitivement

**Filtres utiles :**
- Par statut (pending, approved, rejected)
- Par type de contenu
- Par matière
- Par auteur

### 📌 ModerationRule (Règles de Modération)

**Champs principaux :**
- **Name** : Nom de la règle
- **Description** : Description de la règle
- **Reason** : Raison de la règle
- **Is Active** : Cocher pour activer

**Exemples de règles :**
- **Qualité insuffisante** : Le contenu manque de détails
- **Format incorrect** : Le format ne respecte pas les standards
- **Contenu inapproprié** : Contenu offensant ou inapproprié
- **Duplication** : Contenu déjà existant
- **Erreurs factuelles** : Informations incorrectes

**Workflow :**
1. Créez des règles pour standardiser la modération
2. Utilisez-les lors de la modération du contenu
3. Désactivez les règles obsolètes

**Utilisation :**
- Standardise le processus de modération
- Fournit un feedback clair aux auteurs
- Facilite l'analyse des rejets

---

## Bonnes Pratiques

### 🎯 Création de Contenu

1. **Commencez par les matières**
   - Créez d'abord toutes les matières dans Skills → Subject
   - Utilisez des noms clairs et cohérents

2. **Créez des examens équilibrés**
   - Variez la difficulté des questions
   - Assurez-vous que chaque question a au moins une bonne réponse
   - Testez les examens avant de les publier

3. **Structurez bien les cours et TD**
   - Utilisez des titres hiérarchiques
   - Incluez des exemples concrets
   - Ajoutez des corrections détaillées pour les TD

### 🔐 Sécurité

1. **Gérez les droits avec précaution**
   - N'accordez "Is Superuser" qu'aux administrateurs de confiance
   - Utilisez "Is Staff" pour les modérateurs
   - Désactivez les comptes inactifs

2. **Modérez régulièrement le contenu**
   - Vérifiez la file d'attente quotidiennement
   - Appliquez les règles de manière cohérente
   - Fournissez un feedback constructif

### 📊 Analyse et Monitoring

1. **Surveillez les performances**
   - Consultez régulièrement ExamSession pour identifier les examens problématiques
   - Analysez UserSkill pour comprendre les domaines difficiles
   - Vérifiez XPLog pour détecter les activités anormales

2. **Adaptez les seuils**
   - Ajustez les seuils de badges si trop/pas assez de badges obtenus
   - Modifiez les XP rewards si la progression est trop rapide/lente
   - Révisez les règles de modération si nécessaire

### 🔄 Maintenance

1. **Nettoyez régulièrement**
   - Désactivez les recommandations obsolètes
   - Archivez les anciens ExamSession
   - Supprimez les comptes inactifs après avertissement

2. **Sauvegardez les données**
   - Effectuez des sauvegardes régulières de la base de données
   - Exportez les données importantes périodiquement

---

## 🆘 Dépannage

### Problème : Les examens ne s'affichent pas
**Solution :** Vérifiez que "Is Active" est coché dans l'examen

### Problème : Les utilisateurs ne gagnent pas d'XP
**Solution :** Vérifiez que les services sont correctement appelés dans les vues

### Problème : Les recommandations ne se génèrent pas
**Solution :** Vérifiez que les utilisateurs ont des compétences enregistrées

### Problème : Le contenu communautaire ne s'affiche pas
**Solution :** Vérifiez que le statut est "approved"

### Problème : Erreur "no such table: sessions_cache"
**Solution :** Le cache utilise maintenant le système de fichiers. Vérifiez que le dossier `cache` existe dans le répertoire racine du projet.

---

## ⚡ Optimisations de Performance

### Configuration du Cache
Le système utilise maintenant un cache basé sur fichiers pour améliorer la performance :
- **Cache par défaut** : Stocké dans le dossier `cache/`
- **Cache de sessions** : Sessions stockées dans le cache pour une meilleure performance
- **1000 entrées maximum** : Configuration optimisée pour l'utilisation
- **Pas de surcharge database** : Pas de table de cache database nécessaire

### Optimisations Database
Les requêtes database ont été optimisées avec `select_related` et `prefetch_related` :
- **accounts/views.py** : Optimisation des requêtes pour le dashboard
- **exams/views.py** : Optimisation des requêtes pour les examens
- **community/views.py** : Optimisation des requêtes pour le contenu communautaire
- **Réduction des requêtes N+1** : Meilleure performance globale

### Optimisations CSS
Le CSS a été optimisé pour une meilleure maintenance et performance :
- **Mobile-first approach** : Styles de base pour mobile, améliorations pour écrans plus grands
- **Design tokens** : Variables CSS centralisées pour une maintenance facile
- **Documentation complète** : Commentaires français pour une meilleure compréhension
- **Code propre** : Sections bien organisées et documentées

### Optimisations Assets
- **Images minimales** : Seulement 2 images optimisées (logos)
- **Chargement efficace** : Assets optimisés pour un chargement rapide
- **Fichiers statiques** : Gestion optimisée des fichiers statiques

---

## 📞 Support

Pour toute question ou problème technique :
- Consultez le README principal du projet
- Vérifiez la documentation Django officielle
- Contactez l'équipe de développement

---

**Dernière mise à jour :** 19 Juin 2026
**Version :** 2.0 (Optimisations de performance)
