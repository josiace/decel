"""
Signals Django pour l'application accounts.
Automatise la logique métier liée aux utilisateurs.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import User, Referral, DCTransaction


@receiver(post_save, sender=User)
def create_referral_code(sender, instance, created, **kwargs):
    """
    Génère automatiquement un code de parrainage lors de la création d'un utilisateur.
    """
    if created:
        from .models import Referral
        # Créer une entrée Referral pour l'utilisateur avec son code de parrainage
        referral_code = f"DECEL-{instance.id}-{instance.username[:4].upper()}"
        Referral.objects.create(
            referrer=instance,
            referral_code=referral_code,
            reward_dc=50,
            referred_reward_dc=25
        )


@receiver(post_save, sender=User)
def initialize_user_streak(sender, instance, created, **kwargs):
    """
    Initialise le streak de l'utilisateur lors de la création.
    """
    if created and instance.current_streak == 0:
        instance.current_streak = 0
        instance.longest_streak = 0
        instance.save(update_fields=['current_streak', 'longest_streak'])


@receiver(pre_save, sender=User)
def update_login_stats(sender, instance, **kwargs):
    """
    Met à jour les statistiques de connexion si last_login change.
    """
    if instance.pk:
        try:
            old_instance = User.objects.get(pk=instance.pk)
            if old_instance.last_login != instance.last_login:
                instance.login_count = (old_instance.login_count or 0) + 1
        except User.DoesNotExist:
            pass


@receiver(post_save, sender=Referral)
def award_referral_rewards(sender, instance, created, **kwargs):
    """
    Attribue automatiquement les récompenses de parrainage quand le parrainage est complété.
    """
    if created and instance.is_completed and not instance.completed_at:
        instance.completed_at = timezone.now()
        instance.save(update_fields=['completed_at'])
        
        # Récompense pour le parrain
        if instance.referrer:
            DCTransaction.objects.create(
                user=instance.referrer,
                transaction_type='referral',
                amount=instance.reward_dc,
                balance_after=instance.referrer.dc_balance + instance.reward_dc,
                description=f"Récompense parrainage: {instance.referred.email if instance.referred else 'Utilisateur'}",
                related_content_type='referral',
                related_content_id=instance.id
            )
            instance.referrer.dc_balance += instance.reward_dc
            instance.referrer.save(update_fields=['dc_balance'])
        
        # Récompense pour le filleul
        if instance.referred:
            DCTransaction.objects.create(
                user=instance.referred,
                transaction_type='referral',
                amount=instance.referred_reward_dc,
                balance_after=instance.referred.dc_balance + instance.referred_reward_dc,
                description=f"Bonus parrainage: parrainé par {instance.referrer.email}",
                related_content_type='referral',
                related_content_id=instance.id
            )
            instance.referred.dc_balance += instance.referred_reward_dc
            instance.referred.save(update_fields=['dc_balance'])
