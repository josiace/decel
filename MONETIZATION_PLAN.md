# Plan de Monétisation DECEL



> **Principe fondateur** : monétiser la vitesse et les outils pro, jamais le savoir lui-même.

> L'utilisateur doit pouvoir apprendre et progresser entièrement gratuitement.

> L'argent vient de ceux qui veulent aller plus vite, plus loin, ou contribuer.



---



## Table des matières



1. [Modèle Freemium](#1-modèle-freemium)

2. [Système DC (Decelcone)](#2-système-dc-decelcone)

3. [Abonnement Créateur Pro](#3-abonnement-créateur-pro)

4. [Licences B2B Établissements](#4-licences-b2b-établissements)

5. [Ce qu'il ne faut jamais faire](#5-ce-quil-ne-faut-jamais-faire)

6. [Roadmap d'implémentation](#6-roadmap-dimplémentation)

7. [Intégration paiement](#7-intégration-paiement)

8. [Projections et métriques](#8-projections-et-métriques)



---



## 1. Modèle Freemium



### Règle absolue



Les éléments suivants sont **toujours gratuits**, sans exception :



- Score et résultats de chaque examen

- XP, niveau et progression

- Compétences par matière (UserSkill)

- Contenu de base (cours, TDs, examens gratuits)

- Classements globaux

- Recommandations de base (3 actives)

- Inscription et authentification



### Gratuit vs Premium



| Fonctionnalité | Gratuit | Premium |

|---|---|---|

| Examens de base | ✅ Illimité | — |

| Examens avancés / concours | Limité (3/mois) | ✅ Illimité |

| Cours et TDs gratuits | ✅ Illimité | — |

| Cours premium (PDF annotés) | ❌ | ✅ |

| Recommandations actives | 3 max | ✅ Illimitées + détaillées |

| Classements globaux | ✅ | — |

| Classements par promo / groupe | ❌ | ✅ |

| Dashboard analytique | Basique | ✅ Avancé |

| Streak Shield (protection streak) | ❌ | ✅ 1/mois inclus |

| Badge "Membre Premium" | ❌ | ✅ |

| Support prioritaire | ❌ | ✅ |



### Prix suggéré



| Plan | Prix | Cible |

|---|---|---|

| **Gratuit** | 0 €/mois | Tous les apprenants |

| **Premium Étudiant** | 4,99 €/mois ou 39 €/an | Apprenants actifs |

| **Premium Famille** | 9,99 €/mois (3 comptes) | Familles |



---



## 2. Système DC (Decelcone)



### Principe de double acquisition



Les DC peuvent être obtenus **gratuitement** (fidélité) ou **achetés** (revenus directs).

Les DC gratuits doivent couvrir environ 70 % du contenu disponible.



### DC gratuits (fidélité — déjà implémentés)



| Action | DC gagnés |

|---|---|

| Bonus de connexion quotidienne | +5 DC |

| Bonus streak (1 DC/jour consécutif) | +1 à +10 DC |

| Examen réussi (score ≥ 50 %) | +5 DC |

| Vente d'un contenu créé | +75 % du prix |



### DC achetés (revenus réels — à implémenter)



| Pack | Prix | DC | Valeur unitaire |

|---|---|---|---|

| Starter | 2 € | 100 DC | 0,02 €/DC |

| Populaire ⭐ | 8 € | 500 DC | 0,016 €/DC |

| Meilleur prix | 20 € | 1 500 DC | 0,013 €/DC |

| Pro | 45 € | 4 000 DC | 0,011 €/DC |



### Dépenses DC (déjà modélisées)



- Achat de cours, TDs, corrections premium

- Achat de contenu communautaire payant

- **Streak Shield** : 10 DC pour protéger son streak 1 jour

- **Content Boost** : 50 DC pour mettre en avant son contenu dans les recommandations (à implémenter)



### Règles anti-abus



- Un utilisateur ne peut pas acheter son propre contenu

- Les DC gratuits ne sont pas convertibles en argent réel

- Limite journalière de DC gagnés via examens : 50 DC/jour (anti-farming)

- Plafond du solde DC pour les comptes gratuits : 500 DC



---



## 3. Abonnement Créateur Pro



Les créateurs paient pour des **outils professionnels**, pas pour le droit de publier.

Tout utilisateur peut soumettre du contenu gratuitement.



### Plans créateur



| Plan | Prix | Inclus |

|---|---|---|

| **Créateur Gratuit** | 0 € | Soumettre du contenu, commission 75 %, statistiques basiques |

| **Créateur Pro** | 5 €/mois | Analytics détaillés, badge vérifié ✓, priorité de modération (24 h), export CSV, Content Boost mensuel offert |

| **Académie** | 20 €/mois | Multi-comptes (école/promo), tableau de bord classe, rapports d'élèves PDF, examens privés, priorité modération (12 h) |



### Changements modèle requis (`accounts/models.py`)



```python

class Contributor(models.Model):

    # Champs existants ...



    # À ajouter

    PLAN_CHOICES = [

        ('free', 'Créateur Gratuit'),

        ('pro', 'Créateur Pro'),

        ('academy', 'Académie'),

    ]

    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')

    plan_expires_at = models.DateTimeField(null=True, blank=True)

    stripe_subscription_id = models.CharField(max_length=255, blank=True)

    total_content_sales = models.IntegerField(default=0)

    total_dc_earned = models.IntegerField(default=0)

```



### Avantages pro à implémenter



- **Badge vérifié** : icône ✓ sur le profil et les contenus

- **Analytics créateur** : nombre de vues, achats, revenus DC par contenu

- **Priorité modération** : file de modération séparée pour les pros

- **Content Boost** : 1 boost offert par mois (mise en avant dans les recommandations)



---



## 4. Licences B2B Établissements



C'est le canal de revenus à plus forte valeur. Cela n'impacte pas les utilisateurs individuels.



### Offres



| Offre | Prix | Inclus |

|---|---|---|

| **Classe** | 30 €/mois | Jusqu'à 35 élèves, 1 enseignant, dashboard classe |

| **École** | 100 €/mois | Jusqu'à 200 élèves, 10 enseignants, rapports, examens privés |

| **Institution** | Sur devis | Illimité, white-label, API, support dédié |



### Fonctionnalités B2B à développer



#### Modèles à créer



```python

class Classroom(models.Model):

    name = models.CharField(max_length=255)

    teacher = models.ForeignKey(User, related_name='taught_classrooms', ...)

    students = models.ManyToManyField(User, related_name='classrooms', blank=True)

    institution = models.ForeignKey('Institution', null=True, blank=True, ...)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)



class Institution(models.Model):

    name = models.CharField(max_length=255)

    plan = models.CharField(max_length=20, choices=[('class','Classe'),('school','École'),('institution','Institution')])

    admin_user = models.ForeignKey(User, ...)

    max_students = models.IntegerField(default=35)

    stripe_subscription_id = models.CharField(max_length=255, blank=True)

    plan_expires_at = models.DateTimeField(null=True, blank=True)

```



#### Fonctionnalités dashboard enseignant



- Vue progression de tous les élèves par matière

- Assigner un examen à une classe (examen privé)

- Voir les résultats de la classe en temps réel

- Export rapport PDF / CSV (notes, compétences, progression)

- Comparer la performance d'un élève à la moyenne de la classe



#### Examens privés



```python

# Ajout sur le modèle Exam existant

classroom = models.ForeignKey('Classroom', null=True, blank=True, on_delete=models.SET_NULL)

is_private = models.BooleanField(default=False)

available_from = models.DateTimeField(null=True, blank=True)

available_until = models.DateTimeField(null=True, blank=True)

```



---



## 5. Ce qu'il ne faut jamais faire



Ces pratiques nuisent à la rétention et à la réputation :



| ❌ Pratique interdite | Pourquoi |

|---|---|

| Bloquer les résultats d'examen | Brise la boucle de feedback, frustrant |

| Mettre les XP / niveaux derrière un paywall | Détruit la progression, kill le produit |

| Publicités intrusives | Incompatible avec la concentration nécessaire à l'apprentissage |

| Limiter le nombre d'examens/jour en gratuit | Punit l'assiduité, l'inverse de ce qu'on veut |

| "Vies" à la Duolingo | Artificiel et frustrant pour un public sérieux |

| Pay-to-win sur les classements | Destroy la confiance et la compétition saine |

| Forcer l'upgrade pour voir ses propres compétences | Les skills sont la valeur centrale du produit |

| Email marketing abusif | Désinscriptions en masse |



---



## 6. Roadmap d'implémentation



### Phase 1 — Revenus immédiats (1–2 mois)



Activer ce qui est déjà modélisé dans le code.



- [ ] Page d'achat de packs DC (Stripe Checkout)

- [ ] Webhook Stripe → créditer le solde DC

- [ ] Page historique des transactions DC (`/accounts/wallet/`)

- [ ] Streak Shield (dépense 10 DC, protège le streak 1 jour)

- [ ] Affichage du solde DC dans la navbar



**Revenus attendus** : premiers packs vendus dès le lancement, conversion ~2–5 % des actifs.



### Phase 2 — Abonnement créateur (2–3 mois)



- [ ] Champ `plan` sur `Contributor`

- [ ] Page abonnement Créateur Pro (Stripe Subscriptions)

- [ ] Dashboard analytics créateur (vues, achats, revenus DC)

- [ ] Badge vérifié sur profil et contenus

- [ ] File de modération prioritaire pour les pros

- [ ] Content Boost (mise en avant dans les recommandations)



**Revenus attendus** : MRR stable, surtout si l'audience des créateurs croît.



### Phase 3 — Premium individuel (3–4 mois)



- [ ] Modèle `Subscription` sur `User`

- [ ] Page upgrade Premium Étudiant

- [ ] Recommandations illimitées pour les abonnés

- [ ] Analytics personnel avancé

- [ ] Accès aux examens avancés / concours



**Revenus attendus** : MRR principal à terme.



### Phase 4 — B2B (4–6 mois)



- [ ] Modèles `Classroom` et `Institution`

- [ ] Dashboard enseignant

- [ ] Examens privés par classe

- [ ] Export PDF / CSV des résultats

- [ ] Page commerciale dédiée B2B (`/pro/`)

- [ ] Formulaire de contact / démo pour les institutions



**Revenus attendus** : plus élevés par client, plus stables (contrats annuels).



---



## 7. Intégration paiement



### Solution recommandée



| Région cible | Solution | Pourquoi |

|---|---|---|

| Europe / International | **Stripe** | Documentation excellente, `dj-stripe` pour Django, webhooks fiables |

| Afrique francophone | **CinetPay** ou **PayDunya** | Mobile Money (Orange, MTN, Wave, Moov) |

| Les deux | Stripe + CinetPay | Couverture maximale |



### Packages Django



```

# requirements.txt — à ajouter

dj-stripe>=2.8.0          # Stripe natif Django

stripe>=7.0.0             # SDK Stripe officiel

```



### Architecture des webhooks Stripe



```

Stripe → POST /payments/webhook/

    ├── checkout.session.completed  → créditer DC (achat pack)

    ├── customer.subscription.created → activer abonnement

    ├── customer.subscription.deleted → désactiver abonnement

    └── invoice.payment_failed → notifier l'utilisateur

```



### Sécurité paiements



- Toujours vérifier la signature du webhook Stripe (`stripe.Webhook.construct_event`)

- Ne jamais faire confiance au montant envoyé par le frontend

- Toutes les transactions DC restent atomiques (`@transaction.atomic`)

- Stocker le `stripe_customer_id` sur le modèle `User`

- Ne jamais stocker de numéros de carte (Stripe s'en charge)



---



## 8. Projections et métriques



### KPIs à suivre



| Métrique | Description | Objectif an 1 |

|---|---|---|

| **DAU / MAU ratio** | Rétention quotidienne | > 20 % |

| **Conversion Free → Paid** | % utilisateurs actifs qui paient | 3–8 % |

| **ARPU** | Revenu moyen par utilisateur payant | 6–10 €/mois |

| **MRR** | Revenu mensuel récurrent | Croissance 15 %/mois |

| **Churn rate** | % abonnés qui se désinscrivent | < 5 %/mois |

| **DC spend rate** | % des DC gagnés qui sont dépensés | > 60 % |

| **Créateurs actifs** | Contributeurs ayant publié ce mois | Croissance |



### Hypothèse de revenus (scénario conservateur)



```

1 000 utilisateurs actifs mensuels

  └── 4 % Premium Étudiant (40 users × 4,99 €)  = 200 €/mois

  └── 3 % achètent des DC (30 users × 8 € moy)  = 240 €/mois

  └── 5 créateurs Pro (5 × 5 €)                 = 25 €/mois

  └── 1 licence Classe                           = 30 €/mois

                                          TOTAL  ≈ 495 €/mois



10 000 utilisateurs actifs mensuels → ~4 950 €/mois (MRR)

```



### Levier de croissance principal



Le système de recommandations et de progression est le **meilleur outil de rétention**.

Un utilisateur qui voit ses compétences progresser revient. La monétisation suit la rétention.



---



## Résumé exécutif



```

Court terme  → Activer les packs DC + Stripe (revenus immédiats, faible effort)

Moyen terme  → Abonnement Créateur Pro (MRR stable, ecosystem de contenu)

Long terme   → B2B Licences (tickets élevés, contrats récurrents)



Ce qui ne change pas : le gratuit reste généreux.

La valeur perçue du premium doit être évidente, pas forcée.

```

