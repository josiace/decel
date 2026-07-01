# DECEL - Adaptive Learning Platform

DECEL is a production-grade EdTech SaaS platform that functions as a learning intelligence system. It adapts to user performance through skill tracking, XP progression, and adaptive recommendations.

## 🌐 Public Access & SEO

**Content accessible without registration:**
- Exam listings and details (view-only)
- Course listings and details (view-only)
- TD listings and details (view-only)
- Community content (approved)
- Leaderboards with filters (by country, grade level)
- Blog articles

**SEO Optimizations:**
- Dynamic sitemaps (exams, courses, TDs, corrected TDs, blog, subjects)
- robots.txt configured for public content indexing
- Open Graph and Twitter Card meta tags
- Structured data (Organization, WebSite, SoftwareApplication, FAQPage)
- PWA manifest with multiple icon sizes
- Removed anti-copy protection for better UX

## 🧠 Core Features

### 1. Exam Engine (Strict QCM)
- Multiple choice questions with exact match scoring
- At least one correct answer per question (enforced)
- **Strict scoring**: A question is correct ONLY if `selected_answers == correct_answers`
- No partial scoring allowed
- Server-side validation

### 2. Learning System
- **Courses**: Educational content for learning
- **TD (Travaux Dirigés)**: Practice exercises with self-reported scoring
- **Corrected TD**: TDs with solutions for self-study
- Progress tracking for all content types
- **Content Localization**: Country and grade level targeting for better content relevance
- **Contributor Content Creation**: Web forms for contributors to create courses, TDs, and corrections

### 3. Skill Tracking (Core Intelligence Layer)
- Performance tracking per subject (e.g., Mathematics: 72%, Physics: 45%)
- **Recency weighting**: Recent actions have higher impact on skill calculation
- Skills evolve based on:
  - Exam results
  - TD performance
  - Course engagement

### 4. XP System (Progression Tracking)
- XP is for progression tracking, NOT a currency
- XP rules:
  - Exam completed (passed): 100 XP
  - Exam completed (failed): 50 XP
  - TD completed: 40 XP
  - Course read: 20 XP
- Level calculation: `level = floor(sqrt(total_xp / 100)) + 1`

### 5. DC (Decelcone) Currency System
- DC is the platform currency for purchasing content
- **Separation from XP**: XP is for leveling, DC is for purchases
- **Earning DC**:
  - **Content creators earn 75% commission** when users purchase their content
  - **+5 DC** for each exam passed (score ≥ 50%)
  - **Daily login bonus**: +5 DC + streak bonus (up to +10 DC)
- **Spending DC**:
  - Purchase courses, TDs, and corrections
  - Prices set by admins or content creators
- **Transaction tracking**: All DC transactions recorded in DCTransaction model

### 6. Recommendation Engine
- Adaptive learning suggestions generated after every action
- Recommendation types:
  - **Review**: Suggest revision for weak areas
  - **Advance**: Suggest harder content for strong areas
  - **Practice**: Suggest TD for skill improvement
  - **Learn**: Suggest courses for new topics

### 7. Community Content System
- Users can submit Courses, TDs, and Corrected TDs
- Moderation workflow: DRAFT → PENDING → APPROVED/REJECTED
- Admins can approve/reject content with notes
- Moderation rules for content guidelines

## 🏗️ Architecture

### Django Apps
- **accounts**: Authentication + custom User model + DC currency system
- **exams**: Exam engine with strict QCM evaluation + anti-XP farming
- **learning**: Courses, TDs, Corrected TDs with DC pricing
- **gamification**: XP, levels, badges, leaderboards
- **skills**: User performance tracking per subject
- **recommendations**: Adaptive learning logic engine
- **community**: Content publishing and moderation
- **analytics**: User activity tracking and analytics

### Services Layer (Business Logic)
- **ExamCorrectionService**: Strict QCM scoring and validation
- **SkillService**: Subject skill calculation with recency weighting
- **RecommendationService**: Adaptive learning suggestions
- **XPService**: Progression tracking and level calculation
- **DCService**: DC currency management, transactions, and rewards

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd DECEL
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Frontend: http://127.0.0.1:8000/
   - Admin: http://127.0.0.1:8000/admin/

## 📊 Database Models

### Core Models
- **User** (custom): Email-based auth with XP, level, DC balance, profile fields
- **Subject**: Learning domains (Mathematics, Physics, etc.)
- **Exam**: Complete examinations with questions
- **Question**: Individual QCM questions
- **Choice**: Possible answers for questions
- **ExamSession**: User's attempt at an exam with DC rewards
- **UserAnswer**: User's selected choices per question
- **Course**: Educational content with DC pricing
- **TD**: Practice exercises with DC pricing
- **CorrectedTD**: TD with solutions and DC pricing
- **XPLog**: XP awarded to users
- **DCTransaction**: DC transactions (earnings, spendings, rewards)
- **Badge**: Achievements
- **UserBadge**: Badges earned by users
- **UserSkill**: Performance per subject
- **Recommendation**: Adaptive learning suggestions
- **Content**: Community-submitted content with DC pricing
- **ModerationRule**: Content moderation guidelines

## 🎯 User Flow

### For Non-Registered Users
1. Lands on **home page** (public landing)
2. Can explore:
   - **Exam listings** - View available exams
   - **Course listings** - Browse educational content
   - **TD listings** - Practice exercises
   - **Community content** - Approved user contributions
   - **Leaderboards** - Rankings with filters (country, grade level)
   - **Blog** - Educational articles
3. Registers to access full features

### For Registered Users
1. User logs in
2. Lands on **dashboard** (learning cockpit)
3. User chooses:
   - **Course** (learn) → Updates XP + skill engagement
   - **TD** (practice) → Updates XP + skill based on score
   - **Exam** (test knowledge) → Updates XP + skill + recommendations
4. After ANY action:
   - Log activity
   - Update XP
   - Update skill per subject
   - Generate recommendations
5. Dashboard evolves dynamically:
   - Shows weak subjects
   - Suggests next action
   - Tracks progress evolution

## 🔐 Security Rules

- All exam answers validated server-side
- At least one correct choice per question (enforced)
- Prevent empty or invalid submissions
- Protect exam integrity
- Staff-only moderation access
- **Anti-XP farming**: Exam creators cannot take their own exams

## 🎨 Frontend

- Django templates with Bootstrap 5
- **Mobile-first responsive design** - Optimisé pour tous les appareils
- Clean, modern UI
- Real-time skill visualization
- Progress tracking displays
- **Optimized CSS** - Documentation complète et design tokens centralisés

## ⚡ Performance Optimizations

### CSS Optimizations
- **Mobile-first approach** - Styles de base pour mobile, améliorations pour écrans plus grands
- **Design tokens** - Variables CSS centralisées pour une maintenance facile
- **Code documentation** - Commentaires français pour une meilleure compréhension
- **Clean architecture** - Sections bien organisées et documentées

### Database Optimizations
- **select_related** - Réduction des requêtes N+1 pour les relations ForeignKey
- **prefetch_related** - Optimisation des relations ManyToMany
- **Query optimization** - Vues optimisées dans accounts, exams, et community apps
- **Performance improvement** - Temps de réponse réduits

### Cache Configuration
- **File-based cache** - Cache par défaut basé sur fichiers pour la performance
- **Session cache** - Sessions stockées dans le cache pour une meilleure performance
- **1000 entries max** - Configuration optimisée pour l'utilisation
- **No database overhead** - Pas de table de cache database nécessaire

### Asset Optimization
- **Minimal images** - Seulement 2 images optimisées (logos)
- **Efficient loading** - Assets optimisés pour un chargement rapide
- **Static files** - Gestion optimisée des fichiers statiques

## 📝 Admin Configuration

All models are configured in Django admin with:
- List views with filtering
- Search functionality
- Inline editing where appropriate
- Read-only fields for timestamps

## 🧪 Testing the System

### Creating Test Data via Admin

1. **Create Subjects**
   - Go to Admin → Skills → Subjects
   - Add subjects (e.g., Mathematics, Physics, Chemistry)

2. **Create Exams**
   - Go to Admin → Exams → Exams
   - Add exam with subject, difficulty, passing score
   - Add questions with choices (ensure at least one correct choice)

3. **Create Learning Content**
   - Go to Admin → Learning → Courses/TDs
   - Add content with subject association

4. **Create Badges**
   - Go to Admin → Gamification → Badges
   - Define badge criteria (XP threshold, exam count, skill threshold)

### User Journey

1. Register a new user
2. Take an exam (observe strict QCM scoring)
3. Check dashboard (XP, level, skills updated)
4. View recommendations (adaptive suggestions)
5. Complete a course or TD
6. Observe skill evolution

## 🎓 Key Design Principles

### NOT CRUD
Every feature contributes to learning progression. No isolated CRUD operations.

### Learning Engine First
All data influences:
- User progression
- Skill evolution
- Recommendations

### No Isolated Features
- Exam → updates skills + recommendations
- TD → affects XP + weak areas
- Course → influences recommendations

### Clean Architecture
- Business logic in services layer
- Separation of concerns enforced
- Models for data only
- Views for HTTP handling
- Services for business logic

## 🚧 Future Enhancements

- Real-time exam timer ✅ (implemented)
- Question bank randomization ✅ (implemented)
- Advanced analytics ✅ (implemented)
- Social features (leaderboards, study groups) ✅ (leaderboards implemented)
- Mobile app
- Content versioning ✅ (implemented)
- Advanced recommendation algorithms ✅ (implemented)
- Integration with external content providers
- DC referral system ✅ (implemented)
- DC marketplace for user-to-user transactions
- Content localization (country and grade level) ✅ (implemented)
- Contributor content creation web forms ✅ (implemented)
- Dark mode ✅ (implemented)
- XP evolution charts ✅ (implemented)
- Level progress visualization ✅ (implemented)

## 📄 License

This is a demonstration project for educational purposes.

## 👥 Contributing

This is a reference implementation. Use it as a foundation for building your own adaptive learning platform.
