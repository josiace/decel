# Guide d'Utilisation du Système de Contributeurs

## Vue d'ensemble

Le système de contributeurs permet à l'administrateur de sélectionner des utilisateurs inscrits pour les aider à créer du contenu (cours, examens, contenu communautaire). Chaque contributeur a son propre dashboard personnel.

## Pour l'Administrateur

### Sélectionner un Contributeur

1. Allez dans l'admin Django : `/admin/`
2. Naviguez vers **Accounts** > **Contributeurs**
3. Cliquez sur **"Ajouter contributeur"**
4. Remplissez les informations :
   - **Utilisateur** : Sélectionnez l'utilisateur que vous voulez désigner comme contributeur
   - **Actif** : Cochez pour activer le contributeur (décochez pour désactiver temporairement)
   - **Peut créer des cours** : Cochez si le contributeur peut créer des cours
   - **Peut créer des examens** : Cochez si le contributeur peut créer des examens
   - **Peut créer du contenu communautaire** : Cochez si le contributeur peut créer du contenu communautaire
   - **Créé par** : Laissez vide (sera rempli automatiquement)
5. Cliquez sur **"Enregistrer"**

### Gérer les Contributeurs

- **Liste des contributeurs** : Dans l'admin, vous pouvez voir tous les contributeurs avec leurs permissions
- **Modifier un contributeur** : Cliquez sur un contributeur pour modifier ses permissions
- **Désactiver un contributeur** : Décochez "Actif" pour désactiver temporairement un contributeur
- **Supprimer un contributeur** : Cliquez sur "Supprimer" pour retirer complètement un contributeur

## Pour les Contributeurs

### Accéder au Dashboard

Une fois désigné comme contributeur :
1. Connectez-vous à votre compte
2. Dans la barre de navigation, vous verrez un nouveau lien **"Dashboard Contributeur"**
3. Cliquez pour accéder à votre dashboard personnel

### Dashboard Contributeur

Le dashboard affiche :
- **Statistiques** : Nombre de cours, examens, et contenu communautaire créés
- **Actions rapides** : Liens pour créer rapidement du contenu
- **Contenu récent** : Liste de votre contenu créé récemment

### Créer du Contenu

#### Créer un Cours
1. Dans le dashboard, cliquez sur **"Créer un Cours"** ou allez dans **"Mes Cours"**
2. Remplissez le formulaire web :
   - **Titre** : Nom du cours
   - **Description** : Description détaillée
   - **Matière** : Sélectionnez la matière
   - **Type de contenu** : Texte, PDF ou Image
   - **Contenu (texte)** : Entrez le contenu si type = texte
   - **Fichier** : Uploadez un PDF/image (si type = fichier)
   - **Pays cible** : Sélectionnez le pays cible du cours
   - **Niveau scolaire** : Sélectionnez le niveau (6ème, 5ème, etc.)
   - **Prix en DC** : 0 pour gratuit, sinon le prix en DC
   - **Publier immédiatement** : Cochez pour publier tout de suite
3. Cliquez sur **"Enregistrer"**
4. Le cours sera automatiquement associé à votre compte

#### Modifier un Cours
1. Allez dans **"Mes Cours"**
2. Cliquez sur le cours que vous souhaitez modifier
3. Cliquez sur **"Modifier"**
4. Apportez vos modifications
5. Cliquez sur **"Enregistrer"**

#### Créer un Examen (Interface Intuitive)
1. Dans le dashboard, cliquez sur **"Créer un Examen"** ou allez dans **"Mes Examens"**
2. Remplissez le formulaire :
   - **Titre** : Nom de l'examen
   - **Description** : Description détaillée
   - **Matière** : Sélectionnez la matière
   - **Type d'examen** : Choisissez "Questions sur fichier" ou "Questions manuelles"
   - **Fichier de questions** : Uploadez un PDF/image (si type = fichier)
   - **Difficulté** : Niveau de difficulté (1-5)
   - **Limite de temps** : En minutes (optionnel)
   - **Score de passage** : Pourcentage minimum (ex: 60)
3. Cliquez sur **"Créer l'Examen"**
4. Vous serez redirigé vers la page pour ajouter des questions

#### Ajouter des Questions (Interface Intuitive)
1. Si l'examen est de type "Questions sur fichier", le PDF/image s'affiche
2. Pour ajouter une question :
   - Les options par défaut (A, B, C, D) sont déjà ajoutées
   - Modifiez le label si nécessaire (A, B, C, D, 1, 2, 3, etc.)
   - Entrez le texte de chaque option
   - Cochez **"Correct"** pour les bonnes réponses
   - Cliquez sur **"Ajouter une option"** pour plus d'options
   - Cliquez sur **"Supprimer"** pour retirer une option
3. Cliquez sur **"Ajouter la Question"**
4. Répétez pour chaque question
5. Cliquez sur **"Terminer"** quand vous avez fini

#### Supprimer une Question
1. Dans la liste des questions, cliquez sur **"Supprimer"**
2. Confirmez la suppression

#### Créer un TD (Travaux Dirigés)
1. Dans le dashboard, cliquez sur **"Créer un TD"** ou allez dans **"Mes TDs"**
2. Remplissez le formulaire web :
   - **Titre** : Nom du TD
   - **Description** : Description détaillée
   - **Matière** : Sélectionnez la matière
   - **Type de contenu** : Texte, PDF ou Image
   - **Contenu (texte)** : Entrez le contenu si type = texte
   - **Fichier** : Uploadez un PDF/image (si type = fichier)
   - **Pays cible** : Sélectionnez le pays cible du TD
   - **Niveau scolaire** : Sélectionnez le niveau (6ème, 5ème, etc.)
   - **Prix en DC** : 0 pour gratuit, sinon le prix en DC
   - **Publier immédiatement** : Cochez pour publier tout de suite
3. Cliquez sur **"Enregistrer"**
4. Le TD sera automatiquement associé à votre compte

#### Modifier un TD
1. Allez dans **"Mes TDs"**
2. Cliquez sur le TD que vous souhaitez modifier
3. Cliquez sur **"Modifier"**
4. Apportez vos modifications
5. Cliquez sur **"Enregistrer"**

#### Créer une Correction de TD
1. Dans le dashboard, cliquez sur **"Créer une Correction"** ou allez dans **"Mes Corrections"**
2. Remplissez le formulaire web :
   - **TD associé** : Sélectionnez le TD à corriger
   - **Type de contenu** : Texte, PDF ou Image
   - **Correction (texte)** : Entrez la correction si type = texte
   - **Fichier de correction** : Uploadez un PDF/image (si type = fichier)
   - **Pays cible** : Sélectionnez le pays cible (peut hériter du TD)
   - **Niveau scolaire** : Sélectionnez le niveau (peut hériter du TD)
   - **Prix en DC** : 0 pour gratuit, sinon le prix en DC
3. Cliquez sur **"Enregistrer"**
4. La correction sera automatiquement associée à votre compte

#### Modifier une Correction
1. Allez dans **"Mes Corrections"**
2. Cliquez sur la correction que vous souhaitez modifier
3. Cliquez sur **"Modifier"**
4. Apportez vos modifications
5. Cliquez sur **"Enregistrer"**

#### Créer du Contenu Communautaire
1. Dans le dashboard, cliquez sur **"Créer du Contenu"** ou allez dans **"Mon Contenu Communautaire"**
2. Vous serez redirigé vers le formulaire de création de contenu
3. Remplissez les informations du contenu
4. Le contenu sera automatiquement associé à votre compte

### Voir Votre Contenu

- **Mes Cours** : Liste de tous les cours que vous avez créés
- **Mes TDs** : Liste de tous les TDs que vous avez créés
- **Mes Corrections** : Liste de toutes les corrections que vous avez créées
- **Mes Examens** : Liste de tous les examens que vous avez créés
- **Mon Contenu Communautaire** : Liste de tout le contenu communautaire que vous avez créé

## Permissions

Les contributeurs peuvent avoir des permissions différentes :
- **Peut créer des cours** : Autorise la création de cours
- **Peut créer des examens** : Autorise la création d'examens
- **Peut créer du contenu communautaire** : Autorise la création de contenu communautaire

L'administrateur peut activer ou désactiver chaque permission individuellement pour chaque contributeur.

## Sécurité

- Les contributeurs n'ont pas accès à l'admin Django complet
- Ils ne peuvent créer que le type de contenu pour lequel ils ont la permission
- Le contenu créé est automatiquement associé à leur compte
- L'administrateur peut désactiver un contributeur à tout moment

## Avantages

- **Collaboration** : Permet à plusieurs personnes de créer du contenu
- **Organisation** : Chaque contributeur a son propre dashboard
- **Contrôle** : L'administrateur contrôle exactement ce que chaque contributeur peut faire
- **Traçabilité** : Tout le contenu est associé à son créateur
- **Interface Intuitive** : Création d'examens facile avec JavaScript dynamique
- **Preview du PDF** : Voir le fichier pendant la création des questions
- **Pas de JSON** : Plus besoin de manipuler du JSON manuellement
- **Rapidité** : Ajoutez des options en quelques clics

## Dépannage

### Je ne vois pas le lien "Dashboard Contributeur"
- Vérifiez que vous êtes connecté
- Vérifiez que l'administrateur vous a désigné comme contributeur
- Vérifiez que votre compte de contributeur est actif

### Je ne peux pas créer de cours/examens/contenu
- Vérifiez que l'administrateur vous a donné la permission correspondante
- Contactez l'administrateur si vous pensez qu'il y a une erreur

### Mon contenu n'apparaît pas dans mon dashboard
- Vérifiez que vous avez bien enregistré le contenu
- Vérifiez que le contenu est associé à votre compte
- Contactez l'administrateur si le problème persiste

## Support

Pour toute question ou problème, contactez l'administrateur du système.
