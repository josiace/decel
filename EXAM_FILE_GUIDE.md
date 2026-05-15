# Guide d'Utilisation des Examens sur Fichier

## Vue d'ensemble

Le système d'examens supporte maintenant deux types :
1. **Questions saisies manuellement** : Les questions sont entrées une par une dans l'admin
2. **Questions sur fichier (PDF/Image)** : Les questions sont sur un fichier PDF ou image uploadé

## Créer un Examen sur Fichier

### Étape 1 : Créer l'Examen

1. Allez dans l'admin Django : `/admin/`
2. Naviguez vers **Examens** > **Examens**
3. Cliquez sur **"Ajouter examen"**
4. Remplissez les informations de base :
   - **Titre** : Nom de l'examen
   - **Description** : Description détaillée
   - **Matière** : Sélectionnez la matière
   - **Type d'examen** : Sélectionnez **"Questions sur fichier (PDF/Image)"**
   - **Fichier de questions** : Uploadez votre fichier PDF ou image contenant les questions
   - **Difficulté** : Niveau de difficulté (1-5)
   - **Limite de temps** : Optionnel, en minutes
   - **Note de passage** : Pourcentage minimum pour réussir (ex: 60)
5. Cliquez sur **"Enregistrer"**

### Étape 2 : Créer les Questions

1. Dans l'admin, allez dans **Examens** > **Questions**
2. Cliquez sur **"Ajouter question"**
3. Remplissez :
   - **Examen** : Sélectionnez l'examen créé
   - **Énoncé** : Laissez vide (les questions sont sur le fichier)
   - **Ordre** : Numéro de la question (1, 2, 3, ...)
4. Dans la section **Options de réponse** (en bas de la page), cliquez sur **"Ajouter une autre Option de réponse"**
5. Pour chaque option :
   - **Label** : Sélectionnez le label (A, B, C, D, 1, 2, 3, etc.)
   - **Texte de l'option** : Entrez le texte de l'option
   - **Réponse correcte** : Cochez si cette option est une bonne réponse
   - **Ordre** : Ordre d'affichage (optionnel)
6. Répétez pour toutes les options de cette question
7. Cliquez sur **"Enregistrer"**

### Étape 3 : Répéter pour chaque question

Créez une question pour chaque question sur votre fichier PDF/image avec :
- Le bon ordre (1, 2, 3, etc.)
- Les options de réponse appropriées
- Les bonnes réponses cochées

## Exemple Complet

### Exemple de Fichier PDF

Votre fichier PDF contient :
```
Question 1 : Quelle est la capitale de la France ?
A) Paris
B) Londres
C) Berlin
D) Madrid

Question 2 : Quels sont les pays de l'Union Européenne ?
A) France
B) Suisse
C) Allemagne
D) Norvège
```

### Configuration dans l'Admin

**Question 1 :**
- Ordre : 1
- Énoncé : (vide)
- Options de réponse :
  - Label : A, Texte : "Paris", Réponse correcte : ✅
  - Label : B, Texte : "Londres", Réponse correcte : ❌
  - Label : C, Texte : "Berlin", Réponse correcte : ❌
  - Label : D, Texte : "Madrid", Réponse correcte : ❌

**Question 2 :**
- Ordre : 2
- Énoncé : (vide)
- Options de réponse :
  - Label : A, Texte : "France", Réponse correcte : ✅
  - Label : B, Texte : "Suisse", Réponse correcte : ❌
  - Label : C, Texte : "Allemagne", Réponse correcte : ✅
  - Label : D, Texte : "Norvège", Réponse correcte : ❌

## Labels Disponibles

Vous pouvez utiliser les labels suivants pour vos options :
- **Lettres** : A, B, C, D, E, F
- **Chiffres** : 1, 2, 3, 4, 5, 6

Vous pouvez mélanger lettres et chiffres selon vos besoins.

## Interface Admin

L'interface admin est maintenant entièrement visuelle :
- **Plus de JSON** : Tout se fait via des formulaires
- **Bouton "Ajouter"** : Cliquez pour ajouter une nouvelle option
- **Checkboxes** : Cochez simplement les bonnes réponses
- **Drag & Drop** : Réorganisez les options avec le champ "Ordre"

## Validation

Le système vérifie automatiquement que :
- Chaque question a au moins une option de réponse
- Chaque question a au moins une réponse correcte cochée
- Les labels sont uniques par question (pas deux options "A" pour la même question)

## Expérience Utilisateur

Lorsqu'un utilisateur passe l'examen :
1. Le fichier PDF/image est affiché dans un iframe
2. L'utilisateur peut télécharger le fichier
3. Pour chaque question, les options (A, B, C, D...) sont affichées avec leur texte
4. L'utilisateur sélectionne les bonnes réponses en cochant les cases
5. Le système corrige automatiquement en comparant les sélections avec les réponses correctes

## Avantages

- **Gain de temps** : Plus besoin de saisir chaque question manuellement
- **Flexibilité** : Utilisez vos propres documents PDF ou images
- **Préservation** : Gardez le format original de vos examens
- **Simplicité** : Interface visuelle intuitive, plus de JSON
- **Rapidité** : Ajoutez des options en quelques clics

## Dépannage

### Erreur : "Question doit avoir au moins une option de réponse"
- Ajoutez au moins une option dans la section "Options de réponse"
- Cliquez sur "Ajouter une autre Option de réponse"

### Erreur : "Question doit avoir au moins une réponse correcte"
- Cochez au moins une option comme "Réponse correcte"
- Vérifiez que vous avez coché la checkbox pour les bonnes réponses

### Erreur : "Label doit être unique pour cette question"
- Chaque option doit avoir un label unique (A, B, C, D...)
- Vous ne pouvez pas avoir deux options avec le label "A" pour la même question

### Les options ne s'affichent pas
- Vérifiez que vous avez ajouté des options dans la section "Options de réponse"
- Assurez-vous que l'examen est de type **"Questions sur fichier"**
- Vérifiez que vous avez enregistré la question après avoir ajouté les options

## Support

Pour toute question ou problème, contactez l'administrateur du système.
