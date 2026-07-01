from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from .models import SubscriptionPlan, UserSubscription, SubscriptionTransaction
from accounts.services import DCService


class SubscriptionService:
    """Service pour gérer les abonnements utilisateurs."""
    
    @staticmethod
    @transaction.atomic
    def create_subscription(user, plan_id, payment_method='dc'):
        """
        Crée un nouvel abonnement pour un utilisateur.
        
        Args:
            user: L'utilisateur
            plan_id: ID du plan d'abonnement
            payment_method: Méthode de paiement ('dc' ou 'stripe')
            
        Returns:
            tuple: (success: bool, message: str, subscription: UserSubscription or None)
        """
        from django.utils import timezone
        from datetime import timedelta
        
        plan = SubscriptionPlan.objects.get(id=plan_id)
        
        # Vérifier si l'utilisateur a déjà un abonnement actif
        existing_subscription = UserSubscription.objects.filter(
            user=user,
            status='active'
        ).first()
        
        if existing_subscription and existing_subscription.is_active():
            return False, "Vous avez déjà un abonnement actif. Veuillez d'abord l'annuler.", None
        
        # Calculer la date de fin selon le cycle de facturation
        if plan.billing_cycle == 'monthly':
            end_date = timezone.now() + timedelta(days=30)
        else:  # yearly
            end_date = timezone.now() + timedelta(days=365)
        
        # Déduire les DC si paiement par DC
        if payment_method == 'dc':
            success, message, tx = DCService.deduct_dc(
                user=user,
                amount=plan.dc_price,
                transaction_type='subscription',
                description=f"Abonnement {plan.name} ({plan.get_billing_cycle_display()})"
            )
            
            if not success:
                return False, message, None
        
        # Créer l'abonnement
        subscription = UserSubscription.objects.create(
            user=user,
            plan=plan,
            status='active',
            start_date=timezone.now(),
            end_date=end_date,
            auto_renew=True,
            last_payment_date=timezone.now(),
            next_payment_date=end_date
        )
        
        # Créer la transaction
        SubscriptionTransaction.objects.create(
            user=user,
            subscription=subscription,
            transaction_type='subscription_start',
            dc_amount=plan.dc_price,
            plan_name=plan.name,
            plan_type=plan.plan_type
        )
        
        return True, f"Abonnement {plan.name} créé avec succès !", subscription
    
    @staticmethod
    @transaction.atomic
    def renew_subscription(subscription_id):
        """
        Renouvelle un abonnement existant.
        
        Args:
            subscription_id: ID de l'abonnement
            
        Returns:
            tuple: (success: bool, message: str)
        """
        subscription = UserSubscription.objects.get(id=subscription_id)
        plan = subscription.plan
        
        # Vérifier si l'abonnement est actif
        if not subscription.is_active():
            return False, "Cet abonnement n'est pas actif."
        
        # Déduire les DC
        success, message, tx = DCService.deduct_dc(
            user=subscription.user,
            amount=plan.dc_price,
            transaction_type='subscription',
            description=f"Renouvellement abonnement {plan.name}"
        )
        
        if not success:
            return False, message
        
        # Calculer la nouvelle date de fin
        if plan.billing_cycle == 'monthly':
            subscription.end_date = subscription.end_date + timedelta(days=30)
        else:  # yearly
            subscription.end_date = subscription.end_date + timedelta(days=365)
        
        subscription.last_payment_date = timezone.now()
        subscription.next_payment_date = subscription.end_date
        subscription.save()
        
        # Créer la transaction
        SubscriptionTransaction.objects.create(
            user=subscription.user,
            subscription=subscription,
            transaction_type='subscription_renewal',
            dc_amount=plan.dc_price,
            plan_name=plan.name,
            plan_type=plan.plan_type
        )
        
        return True, "Abonnement renouvelé avec succès !"
    
    @staticmethod
    @transaction.atomic
    def cancel_subscription(subscription_id, reason=""):
        """
        Annule un abonnement.
        
        Args:
            subscription_id: ID de l'abonnement
            reason: Raison de l'annulation
            
        Returns:
            tuple: (success: bool, message: str)
        """
        subscription = UserSubscription.objects.get(id=subscription_id)
        
        if subscription.status == 'cancelled':
            return False, "Cet abonnement est déjà annulé."
        
        subscription.status = 'cancelled'
        subscription.auto_renew = False
        subscription.cancelled_at = timezone.now()
        subscription.cancellation_reason = reason
        subscription.save()
        
        # Créer la transaction
        SubscriptionTransaction.objects.create(
            user=subscription.user,
            subscription=subscription,
            transaction_type='subscription_cancel',
            dc_amount=0,
            plan_name=subscription.plan.name,
            plan_type=subscription.plan.plan_type
        )
        
        return True, "Abonnement annulé avec succès. Vous pourrez continuer à utiliser les fonctionnalités jusqu'à la fin de la période."
    
    @staticmethod
    @transaction.atomic
    def upgrade_subscription(user, new_plan_id):
        """
        Upgrade un abonnement vers un plan supérieur.
        
        Args:
            user: L'utilisateur
            new_plan_id: ID du nouveau plan
            
        Returns:
            tuple: (success: bool, message: str, subscription: UserSubscription or None)
        """
        current_subscription = UserSubscription.objects.filter(
            user=user,
            status='active'
        ).first()
        
        if not current_subscription:
            return False, "Vous n'avez pas d'abonnement actif.", None
        
        new_plan = SubscriptionPlan.objects.get(id=new_plan_id)
        
        # Vérifier que c'est vraiment un upgrade
        if new_plan.dc_price <= current_subscription.plan.dc_price:
            return False, "Le nouveau plan doit être plus cher que l'actuel.", None
        
        # Calculer le prix proratisé
        days_remaining = current_subscription.days_remaining()
        if days_remaining <= 0:
            return False, "Votre abonnement est expiré.", None
        
        # Prix proratisé : différence de prix * (jours restants / 30)
        price_difference = new_plan.dc_price - current_subscription.plan.dc_price
        prorated_price = int(price_difference * (days_remaining / 30))
        
        # Déduire les DC
        success, message, tx = DCService.deduct_dc(
            user=user,
            amount=prorated_price,
            transaction_type='subscription',
            description=f"Upgrade abonnement {current_subscription.plan.name} -> {new_plan.name}"
        )
        
        if not success:
            return False, message, None
        
        # Mettre à jour l'abonnement
        current_subscription.plan = new_plan
        current_subscription.save()
        
        # Créer la transaction
        SubscriptionTransaction.objects.create(
            user=user,
            subscription=current_subscription,
            transaction_type='subscription_upgrade',
            dc_amount=prorated_price,
            plan_name=new_plan.name,
            plan_type=new_plan.plan_type
        )
        
        return True, f"Upgrade vers {new_plan.name} réussi !", current_subscription
    
    @staticmethod
    def get_user_active_subscription(user):
        """
        Récupère l'abonnement actif d'un utilisateur.
        
        Args:
            user: L'utilisateur
            
        Returns:
            UserSubscription or None
        """
        subscription = UserSubscription.objects.filter(
            user=user,
            status='active'
        ).first()
        
        if subscription and subscription.is_active():
            return subscription
        return None
    
    @staticmethod
    def check_subscription_limits(user, limit_type):
        """
        Vérifie si l'utilisateur a atteint sa limite d'abonnement.
        
        Args:
            user: L'utilisateur
            limit_type: Type de limite ('courses', 'exams', 'tds')
            
        Returns:
            tuple: (has_limit: bool, limit: int or None, current: int)
        """
        subscription = SubscriptionService.get_user_active_subscription(user)
        
        if not subscription:
            # Pas d'abonnement = limites par défaut
            return True, 5, 0  # 5 par défaut pour les utilisateurs gratuits
        
        limit = None
        current = 0
        
        if limit_type == 'courses':
            limit = subscription.plan.max_courses_per_month
            if limit:
                from django.utils import timezone
                from datetime import timedelta
                month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                from learning.models import CourseProgress
                current = CourseProgress.objects.filter(
                    user=user,
                    completed_at__gte=month_start
                ).count()
        
        elif limit_type == 'exams':
            limit = subscription.plan.max_exams_per_month
            if limit:
                from django.utils import timezone
                from datetime import timedelta
                month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                from exams.models import ExamSession
                current = ExamSession.objects.filter(
                    user=user,
                    completed_at__gte=month_start
                ).count()
        
        elif limit_type == 'tds':
            limit = subscription.plan.max_tds_per_month
            if limit:
                from django.utils import timezone
                from datetime import timedelta
                month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                from learning.models import TDProgress
                current = TDProgress.objects.filter(
                    user=user,
                    completed_at__gte=month_start
                ).count()
        
        if limit is None:
            return False, None, current  # Pas de limite
        
        return True, limit, current
    
    @staticmethod
    def has_feature(user, feature):
        """
        Vérifie si l'utilisateur a accès à une fonctionnalité premium.
        
        Args:
            user: L'utilisateur
            feature: Nom de la fonctionnalité ('certificates', 'mentoring', 'analytics', 'priority_support', 'ad_free')
            
        Returns:
            bool
        """
        subscription = SubscriptionService.get_user_active_subscription(user)
        
        if not subscription:
            return False
        
        feature_map = {
            'certificates': subscription.plan.has_certificates,
            'mentoring': subscription.plan.has_mentoring,
            'analytics': subscription.plan.has_analytics,
            'priority_support': subscription.plan.has_priority_support,
            'ad_free': subscription.plan.has_ad_free,
        }
        
        return feature_map.get(feature, False)
