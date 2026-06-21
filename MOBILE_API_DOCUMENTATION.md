# DECEL Mobile API Documentation

## 📱 Vue d'ensemble

DECEL est une plateforme d'apprentissage guidé par les données qui permet aux étudiants de passer des examens, d'acheter du contenu éducatif et de suivre leurs compétences. Cette documentation est destinée aux développeurs mobiles qui souhaitent intégrer l'application DECEL.

**URL de base de l'API :** `http://localhost:8000/api/`

**Version de l'API :** v1.0

---

## 🎨 Design System

### Couleurs Principales

```css
--primary-color: #6366f1 (Indigo)
--primary-light: #818cf8
--primary-dark: #4f46e5
--text-primary: #1f2937
--text-secondary: #6b7280
--light-bg: #f9fafb
--border-color: #e5e7eb
```

### Palette de Couleurs

- **Primary (Indigo)** : Actions principales, boutons, liens
- **Success (Green)** : Validation, succès
- **Warning (Orange)** : Avertissements, Orange Money
- **Error (Red)** : Erreurs, suppression
- **Info (Blue)** : Informations, Wave

### Typographie

- **Police** : Sans-serif (Inter, Roboto, ou similaire)
- **Tailles** :
  - H1 : 2rem (32px)
  - H2 : 1.5rem (24px)
  - H3 : 1.25rem (20px)
  - Body : 1rem (16px)
  - Small : 0.875rem (14px)

### Icônes

- **Font Awesome** : Utilisé dans l'interface web
- **Recommandation mobile** : Utiliser Material Icons, Feather Icons ou similaire

### Composants UI

- **Cards** : Coins arrondis (8px), ombre légère
- **Buttons** : Coins arrondis (6px), padding 0.8rem 1.5rem
- **Inputs** : Coins arrondis (6px), bordure 1px
- **Modals** : Fond semi-transparent, coins arrondis (12px)

---

## 🏗️ Structure de l'Application

### Architecture

```
DECEL/
├── accounts/          # Gestion des utilisateurs et DC
├── payments/          # Paiements et packs DC
├── learning/          # Cours et TD
├── exams/            # Examens et sessions
├── community/        # Contenu communautaire
├── gamification/     # XP, badges, leaderboard
├── skills/           # Compétences et sujets
├── analytics/        # Analytics et statistiques
├── contributor/      # Gestion des contributeurs
├── api/              # API REST pour mobile
└── decel/            # Configuration principale
```

### Modèles Principaux

**User (accounts/models.py)**
- `email` : Email unique
- `username` : Nom d'utilisateur
- `first_name`, `last_name` : Nom et prénom
- `dc_balance` : Solde en DC (DevCoins)
- `total_xp` : XP total
- `level` : Niveau de l'utilisateur
- `phone_number` : Numéro de téléphone
- `country` : Pays de l'utilisateur

**DCPack (payments/models.py)**
- `name` : Nom du pack
- `dc_amount` : Montant en DC
- `price_cfa` : Prix en FCFA
- `is_popular` : Pack populaire
- `is_active` : Actif/inactif

**Course (learning/models.py)**
- `title` : Titre du cours
- `description` : Description
- `subject` : Matière associée
- `author` : Auteur (User)
- `dc_price` : Prix en DC
- `content_type` : Type de contenu

**Exam (exams/models.py)**
- `title` : Titre de l'examen
- `subject` : Matière
- `duration_minutes` : Durée en minutes
- `passing_score` : Score minimum pour réussir
- `is_active` : Actif/inactif

---

## 🔐 Authentification

### Token Authentication

L'API utilise l'authentification par token. Chaque requête authentifiée doit inclure le token dans l'en-tête HTTP.

**En-tête d'authentification :**
```
Authorization: Token <votre_token>
```

### Endpoints d'Authentification

#### Inscription

**POST** `/api/auth/register/`

**Corps de la requête :**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "password": "SecurePassword123",
  "password_confirm": "SecurePassword123",
  "phone_number": "+22369549391",
  "country": "Mali"
}
```

**Réponse :**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "dc_balance": 0,
    "total_xp": 0,
    "level": 1,
    "created_at": "2024-01-01T00:00:00Z"
  },
  "token": "abc123def456..."
}
```

#### Connexion

**POST** `/api/auth/login/`

**Corps de la requête :**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

**Réponse :**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "dc_balance": 100,
    "total_xp": 500,
    "level": 2,
    "created_at": "2024-01-01T00:00:00Z"
  },
  "token": "abc123def456..."
}
```

#### Déconnexion

**POST** `/api/auth/logout/`

**En-têtes :**
```
Authorization: Token abc123def456...
```

**Réponse :**
```json
{
  "message": "Déconnexion réussie"
}
```

#### Profil Utilisateur

**GET** `/api/auth/me/`

**En-têtes :**
```
Authorization: Token abc123def456...
```

**Réponse :**
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "dc_balance": 100,
  "total_xp": 500,
  "level": 2,
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

## 💰 Wallet (Portefeuille DC)

### Obtenir le Solde et les Transactions

**GET** `/api/wallet/`

**En-têtes :**
```
Authorization: Token abc123def456...
```

**Réponse :**
```json
{
  "dc_balance": 100,
  "transactions": [
    {
      "id": 1,
      "transaction_type": "purchase",
      "amount": 50,
      "balance_after": 100,
      "description": "Achat pack DC: Pack Standard",
      "created_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "transaction_type": "manual_payment",
      "amount": 100,
      "balance_after": 150,
      "description": "Achat pack DC: Pack Premium",
      "created_at": "2024-01-02T00:00:00Z"
    }
  ]
}
```

### Appliquer un Code de Recharge

**POST** `/api/wallet/apply_code/`

**En-têtes :**
```
Authorization: Token abc123def456...
```

**Corps de la requête :**
```json
{
  "code": "RECHARGE123"
}
```

**Réponse (succès) :**
```json
{
  "message": "Code de recharge appliqué avec succès",
  "dc_amount": 50,
  "new_balance": 150
}
```

**Réponse (erreur) :**
```json
{
  "error": "Code invalide ou expiré"
}
```

---

## 📦 Packs DC

### Lister les Packs Disponibles

**GET** `/api/packs/`

**Réponse :**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Pack Starter",
      "dc_amount": 50,
      "price_cfa": 1000,
      "dc_per_cfa": 0.05,
      "is_popular": false,
      "is_active": true,
      "order": 1
    },
    {
      "id": 2,
      "name": "Pack Standard",
      "dc_amount": 150,
      "price_cfa": 2500,
      "dc_per_cfa": 0.06,
      "is_popular": true,
      "is_active": true,
      "order": 2
    },
    {
      "id": 3,
      "name": "Pack Premium",
      "dc_amount": 500,
      "price_cfa": 7500,
      "dc_per_cfa": 0.067,
      "is_popular": false,
      "is_active": true,
      "order": 3
    }
  ]
}
```

---

## 🛒 Commandes de Packs

### Créer une Commande (Paiement Manuel)

**POST** `/api/orders/`

**En-têtes :**
```
Authorization: Token abc123def456...
```

**Corps de la requête :**
```json
{
  "pack_id": 2,
  "payment_method": "orange_money",
  "transaction_reference": "TXN123456"
}
```

**Méthodes de paiement disponibles :**
- `orange_money` : Orange Money (+223 74 15 20 49)
- `wave` : Wave (+223 69 54 93 91)
- `bank_transfer` : Virement bancaire
- `cash` : Espèces

**Réponse :**
```json
{
  "id": 1,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "dc_balance": 100,
    "total_xp": 500,
    "level": 2,
    "created_at": "2024-01-01T00:00:00Z"
  },
  "pack": {
    "id": 2,
    "name": "Pack Standard",
    "dc_amount": 150,
    "price_cfa": 2500,
    "dc_per_cfa": 0.06,
    "is_popular": true,
    "is_active": true,
    "order": 2
  },
  "dc_amount": 150,
  "price_paid_cfa": 2500,
  "payment_method": "orange_money",
  "status": "pending",
  "created_at": "2024-01-01T00:00:00Z",
  "completed_at": null
}

**Instructions de paiement :**
- **Orange Money** : Envoyez 2500 FCFA au +223 74 15 20 49
- **Wave** : Envoyez 2500 FCFA au +223 69 54 93 91
- **Virement bancaire** : Contactez par email (afletounoudouprince5@gmail.com)
- **Espèces** : Contactez par email (afletounoudouprince5@gmail.com)
```

### Lister les Commandes de l'Utilisateur

**GET** `/api/orders/`

**En-têtes :**
```
Authorization: Token abc123def456...
```

**Réponse :**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": {...},
      "pack": {...},
      "dc_amount": 150,
      "price_paid_cfa": 2500,
      "payment_method": "orange_money",
      "status": "completed",
      "created_at": "2024-01-01T00:00:00Z",
      "completed_at": "2024-01-01T01:00:00Z"
    }
  ]
}
```

**Statuts de commande :**
- `pending` : En attente de validation
- `completed` : Validée et DC crédités
- `rejected` : Rejetée

---

## 📚 Contenu Éducatif

### Cours

**GET** `/api/courses/`

**Réponse :**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Introduction à l'algèbre",
      "description": "Cours d'introduction à l'algèbre linéaire",
      "author": 1,
      "author_name": "John Doe",
      "subject": 1,
      "subject_name": "Mathématiques",
      "content_type": "course",
      "dc_price": 20,
      "is_purchased": false,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### TD (Travaux Dirigés)

**GET** `/api/tds/`

**Réponse :**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "TD Algèbre - Exercices 1-10",
      "description": "Exercices d'algèbre pour débutants",
      "author": 1,
      "author_name": "John Doe",
      "subject": 1,
      "subject_name": "Mathématiques",
      "content_type": "td",
      "dc_price": 10,
      "is_purchased": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Examens

**GET** `/api/exams/`

**En-têtes :**
```
Authorization: Token abc123def456...
```

**Réponse :**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Examen de Mathématiques - Niveau 1",
      "description": "Testez vos connaissances en mathématiques",
      "subject": 1,
      "subject_name": "Mathématiques",
      "duration_minutes": 30,
      "passing_score": 70,
      "question_count": 20,
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Sessions d'Examen

**GET** `/api/exam-sessions/`

**En-têtes :**
```
Authorization: Token abc123def456...
```

**Réponse :**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "exam": {
        "id": 1,
        "title": "Examen de Mathématiques - Niveau 1",
        "description": "Testez vos connaissances en mathématiques",
        "subject": 1,
        "subject_name": "Mathématiques",
        "duration_minutes": 30,
        "passing_score": 70,
        "question_count": 20,
        "is_active": true,
        "created_at": "2024-01-01T00:00:00Z"
      },
      "user": {
        "id": 1,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "dc_balance": 100,
        "total_xp": 500,
        "level": 2,
        "created_at": "2024-01-01T00:00:00Z"
      },
      "score": 85,
      "total_questions": 20,
      "passed": true,
      "started_at": "2024-01-01T00:00:00Z",
      "completed_at": "2024-01-01T00:30:00Z"
    }
  ]
}
```

---

## 🎟️ Codes Promo

### Valider un Code Promo

**POST** `/api/promo-codes/validate/`

**En-têtes :**
```
Authorization: Token abc123def456...
```

**Corps de la requête :**
```json
{
  "code": "PROMO2024"
}
```

**Réponse :**
```json
{
  "code": "PROMO2024",
  "code_type": "percentage",
  "value": 20,
  "is_valid": true,
  "valid_from": "2024-01-01T00:00:00Z",
  "valid_until": "2024-12-31T23:59:59Z"
}
```

**Types de codes :**
- `percentage` : Réduction en pourcentage
- `fixed` : Réduction fixe en FCFA

---

## 👥 Parrainage

### Obtenir le Code de Parrainage

**GET** `/api/referrals/my_code/`

**En-têtes :**
```
Authorization: Token abc123def456...
```

**Réponse :**
```json
{
  "referral_code": "REF123ABC"
}
```

### Lister les Parrainages

**GET** `/api/referrals/`

**En-têtes :**
```
Authorization: Token abc123def456...
```

**Réponse :**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "referral_code": "REF123ABC",
      "referrer_email": "referrer@example.com",
      "referred_email": "referred@example.com",
      "reward_dc": 50,
      "referred_reward_dc": 25,
      "is_completed": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

## ⚠️ Codes d'Erreur

### Codes HTTP

- **200 OK** : Requête réussie
- **201 Created** : Ressource créée
- **400 Bad Request** : Requête invalide
- **401 Unauthorized** : Non authentifié
- **403 Forbidden** : Accès refusé
- **404 Not Found** : Ressource introuvable
- **500 Internal Server Error** : Erreur serveur

### Format d'Erreur

```json
{
  "error": "Message d'erreur"
}
```

### Erreurs Courantes

- **Email ou mot de passe incorrect** : `401 Unauthorized`
- **Code requis** : `400 Bad Request`
- **Code invalide ou expiré** : `400 Bad Request`
- **Pack introuvable** : `404 Not Found`
- **Non authentifié** : `401 Unauthorized`

---

## 📝 Bonnes Pratiques

### Gestion des Tokens

- Stockez le token de manière sécurisée (Keychain/Keystore)
- Renouvelez le token si nécessaire
- Supprimez le token lors de la déconnexion

### Pagination

- Utilisez les paramètres `page` et `page_size`
- Par défaut : 20 items par page
- Maximum : 100 items par page

### Gestion des Erreurs

- Affichez des messages d'erreur clairs à l'utilisateur
- Gérez les erreurs réseau avec retry
- Loggez les erreurs pour le débogage

### Performance

- Utilisez le cache pour les données statiques
- Chargez les images de manière lazy
- Optimisez les requêtes réseau

### Sécurité

- Validez toutes les entrées utilisateur
- Utilisez HTTPS en production
- Ne stockez jamais les mots de passe en clair

---

## 🚀 Exemple d'Implémentation

### React Native (Exemple)

```javascript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// Configuration de l'API
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Ajouter le token aux requêtes
api.interceptors.request.use((config) => {
  const token = AsyncStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

// Inscription
const register = async (userData) => {
  try {
    const response = await api.post('/auth/register/', userData);
    await AsyncStorage.setItem('authToken', response.data.token);
    return response.data;
  } catch (error) {
    throw error;
  }
};

// Connexion
const login = async (email, password) => {
  try {
    const response = await api.post('/auth/login/', { email, password });
    await AsyncStorage.setItem('authToken', response.data.token);
    return response.data;
  } catch (error) {
    throw error;
  }
};

// Obtenir le profil
const getProfile = async () => {
  try {
    const response = await api.get('/auth/me/');
    return response.data;
  } catch (error) {
    throw error;
  }
};

// Obtenir les packs DC
const getPacks = async () => {
  try {
    const response = await api.get('/packs/');
    return response.data;
  } catch (error) {
    throw error;
  }
};

// Créer une commande
const createOrder = async (packId, paymentMethod, transactionReference) => {
  try {
    const response = await api.post('/orders/', {
      pack_id: packId,
      payment_method: paymentMethod,
      transaction_reference: transactionReference,
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};
```

### Flutter (Exemple)

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class ApiService {
  final String baseUrl = 'http://localhost:8000/api';
  String? token;

  Map<String, String> get headers => {
    'Content-Type': 'application/json',
    if (token != null) 'Authorization': 'Token $token',
  };

  // Inscription
  Future<Map<String, dynamic>> register(Map<String, dynamic> userData) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/register/'),
      headers: headers,
      body: jsonEncode(userData),
    );
    
    if (response.statusCode == 201) {
      final data = jsonDecode(response.body);
      token = data['token'];
      return data;
    } else {
      throw Exception('Erreur d\'inscription');
    }
  }

  // Connexion
  Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login/'),
      headers: headers,
      body: jsonEncode({'email': email, 'password': password}),
    );
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      token = data['token'];
      return data;
    } else {
      throw Exception('Erreur de connexion');
    }
  }

  // Obtenir le profil
  Future<Map<String, dynamic>> getProfile() async {
    final response = await http.get(
      Uri.parse('$baseUrl/auth/me/'),
      headers: headers,
    );
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Erreur lors de la récupération du profil');
    }
  }
}
```

---

## 📞 Support

**Contact :**
- Email : afletounoudouprince5@gmail.com
- WhatsApp : +223 69 54 93 91

**Paiements :**
- Orange Money : +223 74 15 20 49
- Wave : +223 69 54 93 91

---

## 📄 Licence

© 2024 DECEL. Tous droits réservés.
