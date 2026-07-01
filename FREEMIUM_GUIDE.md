# Guide de Gestion DECEL - Mode Gratuit vs Payant

## 📋 Table des matières

1. [Ce qui est GRATUIT](#ce-qui-est-gratuit)
2. [Ce qui est PAYANT](#ce-qui-est-payant)
3. [Comment gérer le site](#comment-gérer-le-site)
4. [Administration quotidienne](#administration-quotidienne)
5. [Modération du contenu](#modération-du-contenu)
6. [Support utilisateurs](#support-utilisateurs)
7. [Suivi des revenus](#suivi-des-revenus)

---

## 🆓 Ce qui est GRATUIT

### Pour les visiteurs (non inscrits)
- ✅ **Navigation** - Accès à la landing page
- ✅ **Exploration** - Voir les listes d'examens, cours, TDs
- ✅ **Détails** - Lire les descriptions du contenu
- ✅ **Classements** - Voir les classements publics
- ✅ **Blog** - Lire les articles éducatifs
- ✅ **Communauté** - Voir le contenu approuvé

### Pour les utilisateurs inscrits (gratuit)
- ✅ **Examens QCM** - Passage illimité des examens de base
- ✅ **Résultats** - Voir ses scores et résultats complets
- ✅ **XP et Niveau** - Gagner de l'XP et monter de niveau
- ✅ **Compétences** - Suivi des compétences par matière
- ✅ **Cours gratuits** - Accès aux cours gratuits
- ✅ **TDs gratuits** - Accès aux TDs gratuits
- ✅ **Recommandations** - 3 recommandations actives
- ✅ **Classements** - Classements globaux
- ✅ **DC gratuits** - Gagner des DC via:
  - Bonus de connexion quotidienne (+5 DC)
  - Bonus streak (+1 à +10 DC/jour)
  - Examen réussi (+5 DC)
  - Vente de contenu créé (+75% du prix)
- ✅ **Dashboard** - Tableau de bord basique
- ✅ **Streak** - Série de jours consécutifs
- ✅ **Badges** - Badges de progression

### Pour les créateurs (gratuit)
- ✅ **Soumission** - Soumettre du contenu gratuitement
- ✅ **Vente** - Vendre du contenu et gagner 75% en DC
- ✅ **Statistiques basiques** - Vues et achats de son contenu

---

## 💰 Ce qui est PAYANT

### Packs DC (Monnaie virtuelle)
Les DC s'achètent avec de l'argent réel pour accélérer la progression.

| Pack | Prix | DC | Valeur |
|------|------|-----|--------|
| Starter | 2 € | 100 DC | 0,02 €/DC |
| Populaire ⭐ | 8 € | 500 DC | 0,016 €/DC |
| Meilleur prix | 20 € | 1 500 DC | 0,013 €/DC |
| Pro | 45 € | 4 000 DC | 0,011 €/DC |

### Contenu Premium (payable en DC)
- 📚 **Cours premium** - Cours avec PDF annotés et ressources avancées
- 📝 **TDs premium** - TDs avec corrections détaillées
- ✅ **Corrections payantes** - Corrections de TDs avancés
- 📄 **Contenu communautaire payant** - Contenu créé par d'autres utilisateurs

### Fonctionnalités Premium (payable en DC)
- 🛡️ **Streak Shield** - 10 DC pour protéger son streak 1 jour
- 🚀 **Content Boost** - 50 DC pour mettre en avant son contenu

### Abonnement Créateur Pro (5 €/mois)
- ✅ **Badge vérifié** - Icône ✓ sur le profil
- 📊 **Analytics détaillés** - Vues, achats, revenus par contenu
- ⚡ **Priorité modération** - Modération en 24h
- 📈 **Export CSV** - Exporter ses statistiques
- 🎁 **Content Boost mensuel** - 1 boost offert par mois

### Abonnement Académie (20 €/mois)
- 👥 **Multi-comptes** - Gérer une classe ou promo
- 📋 **Dashboard classe** - Suivi des élèves
- 📄 **Rapports PDF** - Rapports d'élèves
- 🎯 **Examens privés** - Créer des examens pour sa classe
- ⚡ **Priorité modération** - Modération en 12h

### Licences B2B (Établissements)
- 🏫 **Classe** - 30 €/mois (35 élèves, 1 enseignant)
- 🎓 **École** - 100 €/mois (200 élèves, 10 enseignants)
- 🏢 **Institution** - Sur devis (illimité, white-label, API)

---

## 🔧 Comment gérer le site

### 1. Administration Django

**Accès admin:**
```
URL: /admin/
Identifiants: Votre compte superuser
```

**Tâches admin principales:**

#### Gestion des utilisateurs
- **Créer des superusers** pour l'administration
- **Vérifier les comptes** signalés
- **Gérer les bannissements** si nécessaire
- **Attribuer les rôles** (contributor, staff, superuser)

#### Gestion du contenu
- **Examens** - Créer, modifier, désactiver des examens
- **Cours** - Modérer et publier les cours
- **TDs** - Valider les TDs soumis
- **Blog** - Publier des articles
- **Badges** - Créer de nouveaux badges

#### Gestion des paiements
- **Vérifier les transactions** DC
- **Gérer les abonnements** Stripe
- **Rembourser** si nécessaire

### 2. Modération du contenu

**Flux de modération:**

1. **Soumission** - Un utilisateur soumet du contenu
2. **En attente** - Le contenu passe en statut "pending"
3. **Modération** - Un modérateur vérifie:
   - Qualité du contenu
   - Exactitude des informations
   - Respect des règles
4. **Décision** - Approuver ou rejeter
5. **Publication** - Si approuvé, le contenu devient visible

**Règles de modération:**
- ✅ Contenu éducatif et pertinent
- ✅ Informations exactes et vérifiables
- ✅ Respect des droits d'auteur
- ❌ Contenu inapproprié ou offensant
- ❌ Plagiat ou contenu volé
- ❌ Publicité ou spam

### 3. Gestion des classements

**Mise à jour automatique:**
```bash
# Lancer la commande de mise à jour des classements
python manage.py update_leaderboards
```

**Automatisation recommandée:**
```bash
# Ajouter au crontab pour exécution quotidienne
0 */6 * * * cd /path/to/project && python manage.py update_leaderboards
```

### 4. Support utilisateurs

**Canaux de support:**
- 📧 Email: afletounoudouprince5@gmail.com
- 💬 Messages via le dashboard (à implémenter)
- 📱 Formulaire de contact (à implémenter)

**Types de demandes fréquentes:**
- Problèmes de connexion
- Questions sur les paiements
- Signalement de contenu inapproprié
- Demande de remboursement
- Assistance technique

### 5. Analytics et suivi

**Métriques à suivre:**
- 📊 **DAU/MAU** - Utilisateurs actifs quotidiens/mensuels
- 💰 **Conversion** - Taux de conversion gratuit → payant
- 📈 **MRR** - Revenu mensuel récurrent
- 🔄 **Churn rate** - Taux de désabonnement
- 💵 **DC spend rate** - Taux de dépense des DC

**Outils:**
- Django Admin pour les données brutes
- Google Analytics (à intégrer)
- Dashboard analytics (à développer)

---

## 📅 Administration quotidienne

### Matin (9h-10h)
- ✅ Vérifier les soumissions de contenu en attente
- ✅ Modérer le nouveau contenu (priorité aux créateurs Pro)
- ✅ Répondre aux emails de support reçus la veille

### Midi (12h-13h)
- ✅ Vérifier les transactions Stripe du matin
- ✅ Créditer les DC pour les achats validés
- ✅ Surveiller les erreurs ou bugs signalés

### Après-midi (15h-16h)
- ✅ Mettre à jour les classements (si pas automatisé)
- ✅ Analyser les métriques du jour
- ✅ Planifier le contenu du blog pour la semaine

### Soir (18h-19h)
- ✅ Vérifier les modérations restantes
- ✅ Préparer les rapports quotidiens
- ✅ Sauvegarder la base de données (si pas automatisé)

---

## 🛡️ Modération du contenu

### Processus de modération

1. **Accéder au dashboard admin**
2. **Aller dans "Community" → "Content"**
3. **Filtrer par status "pending"**
4. **Réviser chaque contenu:**
   - Lire le contenu
   - Vérifier la qualité
   - Contrôler les sources
5. **Prendre une décision:**
   - Approuver → Changer status en "approved"
   - Rejeter → Changer status en "rejected" + ajouter raison

### Règles d'approbation

**Critères de qualité:**
- Contenu clair et bien structuré
- Informations exactes et vérifiables
- Sources citées si applicable
- Langage approprié
- Formatage correct

**Motifs de rejet:**
- Contenu inexact ou trompeur
- Plagiat évident
- Langage offensant
- Format illisible
- Contenu non éducatif

### Gestion des créateurs Pro

**Priorité de modération:**
- Créateurs Pro: Modération dans les 24h
- Créateurs Académie: Modération dans les 12h
- Créateurs Gratuits: Modération quand possible

**Vérification du badge:**
- Demande de badge vérifié
- Vérifier l'historique du créateur
- Vérifier la qualité du contenu soumis
- Attribuer ou refuser le badge

---

## 📞 Support utilisateurs

### Types de demandes

**1. Problèmes techniques**
- Impossible de se connecter
- Erreur lors d'un examen
- Bug dans l'interface
- Problème de paiement

**Action:**
- Reproduire le problème
- Vérifier les logs
- Corriger ou escalader
- Informer l'utilisateur

**2. Questions sur les fonctionnalités**
- Comment gagner des DC?
- Comment fonctionne le streak?
- Comment devenir créateur?
- Comment acheter un pack DC?

**Action:**
- Répondre avec les informations du guide
- Rediriger vers la documentation
- Proposer une démo si nécessaire

**3. Réclamations**
- Contenu inapproprié
- Comportement abusif d'un utilisateur
- Problème de paiement non reçu

**Action:**
- Enquêter sur la situation
- Prendre les mesures nécessaires
- Informer l'utilisateur de la décision

### Outils de support

**À implémenter:**
- Système de tickets
- Chat en direct
- Base de connaissances
- FAQ interactive

**Pour l'instant:**
- Email: afletounoudouprince5@gmail.com
- Réponse sous 24h

---

## 💵 Suivi des revenus

### Sources de revenus

**1. Ventes de packs DC**
- Suivre le nombre de ventes par pack
- Calculer le revenu mensuel
- Analyser les tendances

**2. Abonnements Créateur Pro**
- Suivre le nombre d'abonnés
- Calculer le MRR (Monthly Recurring Revenue)
- Suivre le churn rate

**3. Licences B2B**
- Suivre les contrats actifs
- Calculer le revenu annuel
- Identifier les opportunités de renouvellement

### Rapports mensuels

**KPIs à inclure:**
- Revenu total du mois
- Nombre d'utilisateurs actifs
- Taux de conversion
- Nombre de créateurs actifs
- Contenu modéré
- Tickets support résolus

**Outils:**
- Export depuis Django Admin
- Dashboard analytics (à développer)
- Rapports automatisés (à implémenter)

---

## 🎯 Recommandations pour maximiser les revenus

### Court terme (1-3 mois)
1. **Activer les packs DC** - Revenus immédiats
2. **Optimiser la landing page** - Améliorer la conversion
3. **Créer du contenu blog** - Attirer du trafic organique
4. **Lancer le programme de parrainage** - Croissance virale

### Moyen terme (3-6 mois)
1. **Lancer Créateur Pro** - MRR stable
2. **Développer les analytics** - Meilleure compréhension des utilisateurs
3. **Optimiser les recommandations** - Meilleure rétention
4. **Lancer les licences B2B** - Revenus élevés

### Long terme (6-12 mois)
1. **Développer l'application mobile** - Accessibilité
2. **Étendre à d'autres pays** - Nouveaux marchés
3. **Partenariats avec écoles** - Distribution B2B
4. **Intelligence artificielle avancée** - Personnalisation

---

## ⚠️ Ce qu'il ne faut JAMAIS faire

| ❌ Pratique interdite | Pourquoi |
|---|---|
| Bloquer les résultats d'examen | Brise la boucle de feedback |
| Mettre les XP derrière un paywall | Détruit la progression |
| Publicités intrusives | Incompatible avec l'apprentissage |
| Limiter les examens/jour en gratuit | Punit l'assiduité |
| "Vies" à la Duolingo | Frustrant pour un public sérieux |
| Pay-to-win sur les classements | Détruit la confiance |
| Forcer l'upgrade pour voir ses compétences | Les skills sont la valeur centrale |

---

## 📞 Contact et support

**Pour toute question sur la gestion du site:**
- 📧 Email: afletounoudouprince5@gmail.com
- 📱 Documentation: Ce guide + MONETIZATION_PLAN.md
- 🔧 Admin Django: /admin/

**Règle d'or:** Le gratuit reste généreux. La valeur perçue du premium doit être évidente, pas forcée.
