"""
Script pour créer des articles de blog exemple pour le SEO.
Exécutez: python manage.py shell < blog/fixtures/sample_blog_posts.py
"""

from django.contrib.auth import get_user_model
from blog.models import BlogPost, BlogCategory

User = get_user_model()

# Créer des catégories
categories_data = [
    {
        'name': 'Apprentissage Adaptatif',
        'description': 'Articles sur l\'apprentissage adaptatif et l\'intelligence artificielle dans l\'éducation.'
    },
    {
        'name': 'Conseils Examens',
        'description': 'Conseils et stratégies pour réussir vos examens et concours.'
    },
    {
        'name': 'Éducation Afrique',
        'description': 'Actualités et analyses sur l\'éducation en Afrique francophone.'
    },
    {
        'name': 'Mathématiques',
        'description': 'Ressources et conseils pour les mathématiques.'
    },
    {
        'name': 'Physique',
        'description': 'Ressources et conseils pour la physique.'
    }
]

for cat_data in categories_data:
    category, created = BlogCategory.objects.get_or_create(
        name=cat_data['name'],
        defaults={'description': cat_data['description']}
    )
    if created:
        print(f"Catégorie créée: {category.name}")

# Créer un utilisateur admin si nécessaire
try:
    admin_user = User.objects.get(email='afletounoudouprince5@gmail.com')
except User.DoesNotExist:
    admin_user = User.objects.create_superuser(
        email='afletounoudouprince5@gmail.com',
        username='admin',
        password='admin123'
    )
    print("Utilisateur admin créé")

# Créer des articles de blog
posts_data = [
    {
        'title': 'Comment l\'apprentissage adaptatif transforme l\'éducation en Afrique',
        'excerpt': 'Découvrez comment l\'intelligence artificielle et l\'apprentissage adaptatif révolutionnent l\'éducation en Afrique francophone.',
        'content': '''L'apprentissage adaptatif est une approche pédagogique révolutionnaire qui utilise l'intelligence artificielle pour personnaliser l'expérience d'apprentissage de chaque étudiant.

En Afrique francophone, cette technologie présente des opportunités uniques pour combler les lacunes du système éducatif traditionnel. Voici comment:

1. **Personnalisation du parcours**: Chaque étudiant progresse à son propre rythme, avec des contenus adaptés à son niveau et à ses besoins spécifiques.

2. **Feedback instantané**: Les étudiants reçoivent des corrections immédiates, ce qui permet de corriger les erreurs avant qu'elles ne s'installent.

3. **Suivi des compétences**: Le système identifie les forces et les faiblesses de chaque élève, permettant un ciblage précis des révisions.

4. **Accessibilité**: Les plateformes d'apprentissage adaptatif sont accessibles partout, réduisant les inégalités d'accès à l'éducation de qualité.

DECEL s'inscrit dans cette vision en offrant une plateforme qui combine examens QCM stricts, suivi des compétences par matière et recommandations personnalisées.

L'avenir de l'éducation en Afrique passe par ces technologies innovantes qui permettent à chaque étudiant de réaliser son plein potentiel.''',
        'meta_description': 'Découvrez comment l\'apprentissage adaptatif transforme l\'éducation en Afrique francophone avec DECEL.',
        'meta_keywords': 'apprentissage adaptatif, IA éducation, Afrique francophone, DECEL, éducation personnalisée',
        'status': 'published',
        'category': 'Apprentissage Adaptatif'
    },
    {
        'title': '5 conseils pour réussir vos examens de mathématiques',
        'excerpt': 'Stratégies éprouvées pour maximiser vos chances de réussite aux examens de mathématiques.',
        'content': '''Les mathématiques sont souvent perçues comme une matière difficile, mais avec les bonnes stratégies, vous pouvez significativement améliorer vos performances.

Voici 5 conseils essentiels:

1. **Comprendre plutôt que mémoriser**: Ne vous contentez pas d'apprendre des formules par cœur. Comprenez la logique derrière chaque concept.

2. **Pratiquez régulièrement**: Les mathématiques se travaillent. Résolvez des exercices quotidiennement pour renforcer vos compétences.

3. **Analysez vos erreurs**: Quand vous vous trompez, comprenez pourquoi. C'est dans l'erreur que se trouve la véritable apprentissage.

4. **Utilisez les examens QCM**: Les plateformes comme DECEL offrent des examens QCM stricts qui vous permettent de tester vos connaissances et d'identifier vos points faibles.

5. **Gérez votre temps**: En examen, la gestion du temps est cruciale. Entraînez-vous à résoudre des problèmes dans un temps limité.

Sur DECEL, vous pouvez pratiquer avec des examens QCM en mathématiques, suivre votre progression par compétence et recevoir des recommandations personnalisées pour améliorer vos performances.

Commencez dès aujourd'hui à appliquer ces conseils et voyez vos notes progresser!''',
        'meta_description': '5 conseils pratiques pour réussir vos examens de mathématiques et améliorer vos notes.',
        'meta_keywords': 'mathématiques, conseils examens, réussite scolaire, DECEL, QCM mathématiques',
        'status': 'published',
        'category': 'Conseils Examens'
    },
    {
        'title': 'L\'avenir de l\'éducation au Mali: défis et opportunités',
        'excerpt': 'Analyse des défis éducatifs au Mali et des opportunités offertes par les technologies numériques.',
        'content': '''Le système éducatif malien fait face à de nombreux défis, mais les technologies numériques offrent des solutions prometteuses.

**Défis actuels:**

- Surcharge des classes
- Manque de ressources pédagogiques
- Inégalités d'accès à l'éducation
- Formation insuffisante des enseignants

**Opportunités numériques:**

1. **Plateformes d'apprentissage en ligne**: Des solutions comme DECEL permettent aux étudiants d'accéder à des contenus de qualité partout au Mali.

2. **Apprentissage adaptatif**: L'IA permet de personnaliser l'apprentissage, compensant le manque d'enseignants qualifiés dans certaines régions.

3. **Évaluation continue**: Les examens en ligne permettent un suivi constant des progrès, identifiant rapidement les élèves en difficulté.

4. **Formation des enseignants**: Les plateformes numériques peuvent également servir à la formation continue des enseignants.

**Le rôle de DECEL:**

DECEL s'engage à contribuer à l'amélioration de l'éducation au Mali en offrant:
- Des examens QCM stricts et fiables
- Un suivi des compétences par matière
- Des recommandations personnalisées
- Un accès gratuit aux fonctionnalités d'apprentissage de base

L'avenir de l'éducation au Mali passe par l'intégration intelligente de ces technologies dans le système éducatif existant.''',
        'meta_description': 'Analyse des défis et opportunités de l\'éducation au Mali avec les technologies numériques.',
        'meta_keywords': 'éducation Mali, Afrique francophone, technologies éducatives, DECEL, apprentissage numérique',
        'status': 'published',
        'category': 'Éducation Afrique'
    },
    {
        'title': 'Les bases de la physique pour les débutants',
        'excerpt': 'Guide complet pour comprendre les concepts fondamentaux de la physique.',
        'content': '''La physique est la science qui étudie les propriétés de la matière, de l'énergie et leurs interactions. Pour les débutants, voici les concepts essentiels à maîtriser.

**1. Les grandeurs physiques fondamentales:**

- **Masse**: Quantité de matière (kg)
- **Longueur**: Distance (m)
- **Temps**: Durée (s)
- **Température**: Degré de chaleur (K)
- **Intensité électrique**: Flux d'électrons (A)

**2. Les lois de Newton:**

- **Première loi**: Un objet au repos reste au repos, un objet en mouvement reste en mouvement à moins qu'une force n'agisse sur lui.
- **Deuxième loi**: F = ma (Force = masse × accélération)
- **Troisième loi**: Pour chaque action, il y a une réaction égale et opposée.

**3. L'énergie:**

- **Énergie cinétique**: Énergie du mouvement (½mv²)
- **Énergie potentielle**: Énergie stockée (mgh)
- **Conservation de l'énergie**: L'énergie ne peut être ni créée ni détruite, seulement transformée.

**Comment pratiquer sur DECEL:**

Utilisez nos examens QCM en physique pour tester vos connaissances, identifier vos points faibles et suivre votre progression par compétence. La pratique régulière est la clé de la réussite en physique!

Commencez par les concepts de base et progressez graduellement vers des sujets plus complexes. N'hésitez pas à revoir les fondamentaux si nécessaire.''',
        'meta_description': 'Guide complet des concepts fondamentaux de la physique pour les débutants.',
        'meta_keywords': 'physique, concepts fondamentaux, lois Newton, énergie, DECEL, examens physique',
        'status': 'published',
        'category': 'Physique'
    },
    {
        'title': 'Comment utiliser DECEL pour préparer le BAC',
        'excerpt': 'Guide complet pour utiliser DECEL efficacement dans votre préparation au Baccalauréat.',
        'content': '''Le Baccalauréat est un examen crucial qui détermine votre avenir académique. DECEL peut être un outil puissant pour votre préparation.

**Étape 1: Évaluez votre niveau actuel**

Commencez par passer des examens QCM dans chaque matière pour identifier vos forces et faiblesses. DECEL vous donnera un aperçu de vos compétences par matière.

**Étape 2: Créez un plan d'étude**

Basé sur vos résultats, concentrez-vous sur:
- Les matières où vous avez des lacunes
- Les sujets spécifiques où vous échouez souvent
- Les compétences à renforcer

**Étape 3: Pratiquez régulièrement**

- Passez 2-3 examens QCM par semaine
- Utilisez les cours et TD pour réviser les concepts
- Suivez votre progression dans le tableau de bord

**Étape 4: Analysez vos erreurs**

Quand vous ratez un examen:
- Comprenez pourquoi vous vous êtes trompé
- Revevez les concepts correspondants
- Refaites des exercices similaires

**Étape 5: Utilisez les recommandations**

DECEL génère des recommandations personnalisées basées sur vos performances. Suivez-les pour optimiser votre temps d'étude.

**Conseils supplémentaires:**

- Commencez tôt (au moins 3 mois avant le BAC)
- Maintenez une série d'apprentissage (streak)
- Utilisez les badges pour rester motivé
- Rejoignez le classement pour vous comparer aux autres

Avec DECEL, vous avez tous les outils pour réussir votre BAC. Commencez dès aujourd'hui!''',
        'meta_description': 'Guide complet pour utiliser DECEL efficacement dans la préparation au Baccalauréat.',
        'meta_keywords': 'BAC, préparation examen, DECEL, réussite scolaire, baccalauréat Mali, conseils révision',
        'status': 'published',
        'category': 'Conseils Examens'
    }
]

for post_data in posts_data:
    category = BlogCategory.objects.get(name=post_data['category'])
    
    post, created = BlogPost.objects.get_or_create(
        title=post_data['title'],
        defaults={
            'slug': post_data['title'].lower().replace(' ', '-').replace("'", '-'),
            'author': admin_user,
            'content': post_data['content'],
            'excerpt': post_data['excerpt'],
            'meta_description': post_data['meta_description'],
            'meta_keywords': post_data['meta_keywords'],
            'status': post_data['status'],
        }
    )
    
    if created:
        print(f"Article créé: {post.title}")
    else:
        print(f"Article existe déjà: {post.title}")

print("\nCréation des articles de blog terminée!")
