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
        if creator_share > 0 and author != purchaser:
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

    @staticmethod
    def get_user_earnings(user):
        """
        Calcule les gains totaux d'un utilisateur.
        
        Args:
            user: L'utilisateur
            
        Returns:
            dict: Dictionnaire avec les gains par type
        """
        transactions = DCTransaction.objects.filter(user=user, amount__gt=0)
        
        earnings = {
            'total': transactions.aggregate(total=models.Sum('amount'))['total'] or 0,
            'sales': transactions.filter(transaction_type='sale').aggregate(total=models.Sum('amount'))['total'] or 0,
            'exam_rewards': transactions.filter(transaction_type='exam_reward').aggregate(total=models.Sum('amount'))['total'] or 0,
            'daily_bonuses': transactions.filter(transaction_type='daily_bonus').aggregate(total=models.Sum('amount'))['total'] or 0,
            'referrals': transactions.filter(transaction_type='referral').aggregate(total=models.Sum('amount'))['total'] or 0,
        }
        
        return earnings
