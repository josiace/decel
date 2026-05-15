from django.db import transaction
from django.contrib import messages
from .models import Course, TD, CorrectedTD, ContentPurchase
from gamification.services import XPService


class ContentPurchaseService:
    """Service pour gérer les achats de contenu en XP."""
    
    @staticmethod
    def has_purchased(user, content_type, content_id):
        """Vérifie si l'utilisateur a déjà acheté le contenu."""
        if content_type == 'course':
            return ContentPurchase.objects.filter(
                user=user,
                content_type='course',
                course_id=content_id
            ).exists()
        elif content_type == 'td':
            return ContentPurchase.objects.filter(
                user=user,
                content_type='td',
                td_id=content_id
            ).exists()
        elif content_type == 'corrected_td':
            return ContentPurchase.objects.filter(
                user=user,
                content_type='corrected_td',
                corrected_td_id=content_id
            ).exists()
        return False
    
    @staticmethod
    def get_content_price(content_type, content_id):
        """Récupère le prix en XP du contenu."""
        if content_type == 'course':
            course = Course.objects.get(id=content_id)
            return course.xp_price
        elif content_type == 'td':
            td = TD.objects.get(id=content_id)
            return td.xp_price
        elif content_type == 'corrected_td':
            corrected_td = CorrectedTD.objects.get(id=content_id)
            return corrected_td.xp_price
        return 0
    
    @staticmethod
    @transaction.atomic
    def purchase_content(user, content_type, content_id):
        """Achète du contenu en XP."""
        price = ContentPurchaseService.get_content_price(content_type, content_id)
        
        if price == 0:
            return True, "Contenu gratuit"
        
        if user.total_xp < price:
            return False, f"XP insuffisant. Vous avez {user.total_xp} XP, mais il faut {price} XP."
        
        if ContentPurchaseService.has_purchased(user, content_type, content_id):
            return False, "Vous avez déjà acheté ce contenu."
        
        # Débiter l'XP
        user.total_xp -= price
        user.save()
        
        # Enregistrer l'achat
        purchase = ContentPurchase.objects.create(
            user=user,
            content_type=content_type,
            xp_paid=price
        )
        
        if content_type == 'course':
            purchase.course_id = content_id
        elif content_type == 'td':
            purchase.td_id = content_id
        elif content_type == 'corrected_td':
            purchase.corrected_td_id = content_id
        
        purchase.save()
        
        # Enregistrer le log XP
        XPService.award_xp(
            user=user,
            amount=-price,
            reason=f"Achat de contenu ({content_type})",
            action_type='purchase'
        )
        
        return True, f"Contenu acheté avec succès pour {price} XP."
    
    @staticmethod
    def can_access(user, content_type, content_id, price):
        """Vérifie si l'utilisateur peut accéder au contenu."""
        if price == 0:
            return True
        return ContentPurchaseService.has_purchased(user, content_type, content_id)
