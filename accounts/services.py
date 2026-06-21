from django.db import transaction
from .models import User, DCTransaction


class DCService:
    """Service pour gérer les transactions DC (Decelcone)."""

    CREATOR_COMMISSION = 0.75  # 75% du prix va au créateur
    EXAM_REWARD = 5  # 5 DC par examen réussi
    DAILY_LOGIN_BONUS = 5  # 5 DC par jour de connexion

    @staticmethod
    @transaction.atomic
    def add_dc(user, amount, transaction_type, description, content_type=None, content_id=None):
        """
        Ajoute des DC au solde de l'utilisateur et enregistre la transaction.

        Args:
            user: L'utilisateur
            amount: Montant à ajouter (positif)
            transaction_type: Type de transaction (sale, exam_reward, daily_bonus, etc.)
            description: Description de la transaction
            content_type: Type de contenu lié (optionnel)
            content_id: ID du contenu lié (optionnel)

        Returns:
            DCTransaction: La transaction créée
        """
        user.dc_balance += amount
        user.save()

        dc_transaction = DCTransaction.objects.create(
            user=user,
            transaction_type=transaction_type,
            amount=amount,
            balance_after=user.dc_balance,
            description=description,
            related_content_type=content_type or '',
            related_content_id=content_id
        )

        return dc_transaction

    @staticmethod
    @transaction.atomic
    def deduct_dc(user, amount, transaction_type, description, content_type=None, content_id=None):
        """
        Déduit des DC du solde de l'utilisateur et enregistre la transaction.

        Args:
            user: L'utilisateur
            amount: Montant à déduire (positif)
            transaction_type: Type de transaction (purchase, admin_deduct, etc.)
            description: Description de la transaction
            content_type: Type de contenu lié (optionnel)
            content_id: ID du contenu lié (optionnel)

        Returns:
            tuple: (success: bool, message: str, transaction: DCTransaction or None)
        """
        if user.dc_balance < amount:
            return False, f"Solde DC insuffisant. Vous avez {user.dc_balance} DC, mais il faut {amount} DC.", None

        user.dc_balance -= amount
        user.save()

        dc_transaction = DCTransaction.objects.create(
            user=user,
            transaction_type=transaction_type,
            amount=-amount,
            balance_after=user.dc_balance,
            description=description,
            related_content_type=content_type or '',
            related_content_id=content_id
        )

        return True, "Transaction réussie", dc_transaction

    @staticmethod
    @transaction.atomic
    def process_content_purchase(purchaser, content_type, content_id, price, author):
        """
        Traite un achat de contenu : débite l'acheteur et crédite le créateur.

        Args:
            purchaser: L'utilisateur qui achète
            content_type: Type de contenu (course, td, corrected_td, community_content)
            content_id: ID du contenu
            price: Prix en DC
            author: Le créateur du contenu

        Returns:
            tuple: (success: bool, message: str)
        """
        if price == 0:
            return True, "Contenu gratuit"

        # Débiter l'acheteur
        success, message, purchase_transaction = DCService.deduct_dc(
            user=purchaser,
            amount=price,
            transaction_type='purchase',
            description=f"Achat de {content_type} #{content_id}",
            content_type=content_type,
            content_id=content_id
        )

        if not success:
            return False, message

        # Créditer le créateur (75% de commission)
        creator_share = int(price * DCService.CREATOR_COMMISSION)
        if creator_share > 0 and author and author != purchaser:
            DCService.add_dc(
                user=author,
                amount=creator_share,
                transaction_type='sale',
                description=f"Vente de {content_type} #{content_id} à {purchaser.email}",
                content_type=content_type,
                content_id=content_id
            )

        return True, f"Achat réussi pour {price} DC"

    @staticmethod
    @transaction.atomic
    def award_exam_reward(user, exam_id, score):
        """
        Récompense l'utilisateur pour avoir réussi un examen.

        Args:
            user: L'utilisateur
            exam_id: ID de l'examen
            score: Score obtenu

        Returns:
            DCTransaction: La transaction créée
        """
        # Récompenser seulement si score >= 50%
        if score >= 50:
            return DCService.add_dc(
                user=user,
                amount=DCService.EXAM_REWARD,
                transaction_type='exam_reward',
                description=f"Récompense examen #{exam_id} - Score: {score}%",
                content_type='exam',
                content_id=exam_id
            )
        return None

    @staticmethod
    @transaction.atomic
    def award_daily_bonus(user):
        """
        Récompense l'utilisateur pour sa connexion quotidienne.

        Args:
            user: L'utilisateur

        Returns:
            tuple: (success: bool, message: str, transaction: DCTransaction or None)
        """
        # Vérifier si l'utilisateur a déjà reçu le bonus aujourd'hui
        from django.utils import timezone
        from datetime import date

        today = date.today()
        existing_bonus = DCTransaction.objects.filter(
            user=user,
            transaction_type='daily_bonus',
            created_at__date=today
        ).exists()

        if existing_bonus:
            return False, "Bonus quotidien déjà reçu aujourd'hui", None

        # Bonus de streak : +1 DC pour chaque jour consécutif jusqu'à 10
        streak_bonus = min(user.current_streak, 10)
        total_bonus = DCService.DAILY_LOGIN_BONUS + streak_bonus

        transaction = DCService.add_dc(
            user=user,
            amount=total_bonus,
            transaction_type='daily_bonus',
            description=f"Bonus quotidien (streak: {user.current_streak} jours)"
        )

        return True, f"Bonus quotidien de {total_bonus} DC reçu !", transaction

    @staticmethod
    def get_user_transactions(user, limit=50):
        """
        Récupère l'historique des transactions DC d'un utilisateur.

        Args:
            user: L'utilisateur
            limit: Nombre maximum de transactions à retourner

        Returns:
            QuerySet: Les transactions de l'utilisateur
        """
        return DCTransaction.objects.filter(user=user).order_by('-created_at')[:limit]

    STREAK_SHIELD_COST = 10  # DC requis pour activer le Streak Shield

    @staticmethod
    @transaction.atomic
    def activate_streak_shield(user):
        """
        Dépense 10 DC pour protéger le streak de l'utilisateur pour aujourd'hui.

        Returns:
            tuple: (success: bool, message: str)
        """
        from datetime import date

        today = date.today()

        # Déjà actif aujourd'hui
        if user.streak_shield_active_until and user.streak_shield_active_until >= today:
            return False, "Le Streak Shield est déjà actif aujourd'hui."

        success, message, tx = DCService.deduct_dc(
            user=user,
            amount=DCService.STREAK_SHIELD_COST,
            transaction_type='streak_shield',
            description="Streak Shield — protection du streak pour aujourd'hui"
        )

        if success:
            user.streak_shield_active_until = today
            user.save()
            return True, "Streak Shield activé avec succès !"
        return False, message


class ReferralService:
    """Service pour gérer le système de parrainage."""

    REFERRAL_REWARD = 50  # DC donnés au parrain
    REFERRED_REWARD = 25  # DC donnés au filleul
    REFERRAL_CODE_LENGTH = 8  # Longueur du code de parrainage

    @staticmethod
    def generate_referral_code():
        """Génère un code de parrainage unique."""
        import random
        import string
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=ReferralService.REFERRAL_CODE_LENGTH))
            from .models import Referral
            if not Referral.objects.filter(referral_code=code).exists():
                return code

    @staticmethod
    @transaction.atomic
    def create_referral(referrer, referral_code=None):
        """
        Crée un code de parrainage pour un utilisateur.

        Args:
            referrer: L'utilisateur qui parraine
            referral_code: Code de parrainage personnalisé (optionnel)

        Returns:
            Referral: L'objet Referral créé
        """
        from .models import Referral
        
        if referral_code is None:
            referral_code = ReferralService.generate_referral_code()
        
        # Vérifier si l'utilisateur a déjà un code de parrainage
        if Referral.objects.filter(referrer=referrer).exists():
            return Referral.objects.filter(referrer=referrer).first()
        
        referral = Referral.objects.create(
            referrer=referrer,
            referral_code=referral_code,
            reward_dc=ReferralService.REFERRAL_REWARD,
            referred_reward_dc=ReferralService.REFERRED_REWARD
        )
        return referral

    @staticmethod
    @transaction.atomic
    def process_referral(referral_code, referred_user):
        """
        Traite un parrainage quand un nouveau utilisateur s'inscrit avec un code.

        Args:
            referral_code: Le code de parrainage utilisé
            referred_user: L'utilisateur qui s'est inscrit (filleul)

        Returns:
            tuple: (success: bool, message: str, referral: Referral or None)
        """
        from .models import Referral
        
        try:
            referral = Referral.objects.get(referral_code=referral_code)
            
            # Vérifier que le filleul n'est pas déjà parrainé
            if Referral.objects.filter(referred=referred_user).exists():
                return False, "Vous avez déjà utilisé un code de parrainage.", None
            
            # Vérifier que le parrain ne se parraine pas lui-même
            if referral.referrer == referred_user:
                return False, "Vous ne pouvez pas utiliser votre propre code de parrainage.", None
            
            # Créer le lien de parrainage
            referral.referred = referred_user
            referral.save()
            
            # Donner la récompense au filleul
            DCService.add_dc(
                user=referred_user,
                amount=referral.referred_reward_dc,
                transaction_type='referral',
                description=f"Bienvenue ! Bonus de parrainage de {referral.referred_reward_dc} DC"
            )
            
            # Donner la récompense au parrain
            DCService.add_dc(
                user=referral.referrer,
                amount=referral.reward_dc,
                transaction_type='referral',
                description=f"Parrainage : {referred_user.email} a utilisé votre code"
            )
            
            return True, f"Félicitations ! Vous avez reçu {referral.referred_reward_dc} DC de bienvenue !", referral
            
        except Referral.DoesNotExist:
            return False, "Code de parrainage invalide.", None

    @staticmethod
    def get_referral_stats(user):
        """
        Récupère les statistiques de parrainage d'un utilisateur.

        Args:
            user: L'utilisateur

        Returns:
            dict: Statistiques de parrainage
        """
        from .models import Referral
        from django.db.models import Sum
        
        referrals_made = Referral.objects.filter(referrer=user)
        completed_referrals = referrals_made.filter(is_completed=True)
        
        total_earned = referrals_made.aggregate(
            total=Sum('reward_dc')
        )['total'] or 0
        
        return {
            'total_referrals': referrals_made.count(),
            'completed_referrals': completed_referrals.count(),
            'total_earned_dc': total_earned,
            'referral_code': referrals_made.first().referral_code if referrals_made.exists() else None
        }


class PromoCodeService:
    """Service pour gérer les codes promotionnels."""

    @staticmethod
    @transaction.atomic
    def create_promo_code(code, code_type, value, valid_from, valid_until, max_uses=None, description="", created_by=None):
        """
        Crée un nouveau code promo.

        Args:
            code: Le code promo
            code_type: Type de code (dc_bonus, xp_boost, discount, special)
            value: Valeur du code
            valid_from: Date de début de validité
            valid_until: Date de fin de validité
            max_uses: Nombre maximum d'utilisations (optionnel)
            description: Description du code
            created_by: Utilisateur qui a créé le code

        Returns:
            PromoCode: L'objet PromoCode créé
        """
        from .models import PromoCode
        
        promo_code = PromoCode.objects.create(
            code=code.upper(),
            code_type=code_type,
            value=value,
            max_uses=max_uses,
            valid_from=valid_from,
            valid_until=valid_until,
            description=description,
            created_by=created_by
        )
        return promo_code

    @staticmethod
    @transaction.atomic
    def apply_promo_code(user, code):
        """
        Applique un code promo à un utilisateur.

        Args:
            user: L'utilisateur
            code: Le code promo à appliquer

        Returns:
            tuple: (success: bool, message: str, reward_given: int)
        """
        from .models import PromoCode, PromoCodeUsage
        from django.utils import timezone
        
        try:
            promo_code = PromoCode.objects.get(code__iexact=code)
            
            # Vérifier si le code est valide
            if not promo_code.is_valid():
                if not promo_code.is_active:
                    return False, "Ce code promo n'est plus actif.", 0
                if promo_code.valid_from > timezone.now():
                    return False, "Ce code promo n'est pas encore valide.", 0
                if promo_code.valid_until < timezone.now():
                    return False, "Ce code promo a expiré.", 0
                if promo_code.max_uses and promo_code.used_count >= promo_code.max_uses:
                    return False, "Ce code promo a atteint sa limite d'utilisations.", 0
            
            # Vérifier si l'utilisateur a déjà utilisé ce code
            if PromoCodeUsage.objects.filter(promo_code=promo_code, user=user).exists():
                return False, "Vous avez déjà utilisé ce code promo.", 0
            
            reward_given = 0
            
            # Appliquer la récompense selon le type
            if promo_code.code_type == 'dc_bonus':
                DCService.add_dc(
                    user=user,
                    amount=promo_code.value,
                    transaction_type='admin_grant',
                    description=f"Code promo : {promo_code.code}"
                )
                reward_given = promo_code.value
                
            elif promo_code.code_type == 'xp_boost':
                from gamification.services import XPService
                XPService.award_xp(
                    user=user,
                    amount=promo_code.value,
                    reason=f"Code promo : {promo_code.code}",
                    action_type='promo_code'
                )
                reward_given = promo_code.value
            
            elif promo_code.code_type == 'special':
                # Pour les codes spéciaux, on peut ajouter une logique personnalisée
                DCService.add_dc(
                    user=user,
                    amount=promo_code.value,
                    transaction_type='admin_grant',
                    description=f"Code promo spécial : {promo_code.code}"
                )
                reward_given = promo_code.value
            
            # Enregistrer l'utilisation
            PromoCodeUsage.objects.create(
                promo_code=promo_code,
                user=user,
                reward_given=reward_given
            )
            
            # Incrémenter le compteur d'utilisations
            promo_code.used_count += 1
            promo_code.save()
            
            return True, f"Code promo appliqué ! Vous avez reçu {reward_given} {'DC' if promo_code.code_type in ['dc_bonus', 'special'] else 'XP'}.", reward_given
            
        except PromoCode.DoesNotExist:
            return False, "Code promo invalide.", 0

    @staticmethod
    def get_user_promo_usages(user):
        """
        Récupère les utilisations de codes promo d'un utilisateur.

        Args:
            user: L'utilisateur

        Returns:
            QuerySet: Les utilisations de codes promo de l'utilisateur
        """
        from .models import PromoCodeUsage
        return PromoCodeUsage.objects.filter(user=user).select_related('promo_code').order_by('-used_at')
