from django.db import transaction
from django.contrib import messages
from .models import Course, TD, CorrectedTD, ContentPurchase, ContentVersion
from gamification.services import XPService
from accounts.services import DCService, PromoCodeService


class ContentPurchaseService:
    """Service pour gérer les achats de contenu en DC."""
    
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
        """Récupère le prix en DC du contenu."""
        if content_type == 'course':
            course = Course.objects.get(id=content_id)
            return course.dc_price
        elif content_type == 'td':
            td = TD.objects.get(id=content_id)
            return td.dc_price
        elif content_type == 'corrected_td':
            corrected_td = CorrectedTD.objects.get(id=content_id)
            return corrected_td.dc_price
        return 0
    
    @staticmethod
    @transaction.atomic
    def purchase_content(user, content_type, content_id, promo_code=None):
        """Achète du contenu en DC avec option de code promo."""
        price = ContentPurchaseService.get_content_price(content_type, content_id)
        
        if price == 0:
            return True, "Contenu gratuit"
        
        if ContentPurchaseService.has_purchased(user, content_type, content_id):
            return False, "Vous avez déjà acheté ce contenu."
        
        # Appliquer le code promo si fourni
        discount = 0
        if promo_code:
            success, message, discount_amount = PromoCodeService.apply_promo_code(user, promo_code)
            if success:
                discount = discount_amount
            else:
                return False, message
        
        # Calculer le prix après réduction
        final_price = max(0, price - discount)
        
        # Récupérer l'auteur du contenu
        author = None
        if content_type == 'course':
            course = Course.objects.get(id=content_id)
            author = course.author
        elif content_type == 'td':
            td = TD.objects.get(id=content_id)
            author = td.author
        elif content_type == 'corrected_td':
            corrected_td = CorrectedTD.objects.get(id=content_id)
            author = None  # Les corrections n'ont pas d'auteur direct
        
        # Traiter l'achat avec DCService (débiter acheteur, créditer créateur)
        success, message = DCService.process_content_purchase(
            purchaser=user,
            content_type=content_type,
            content_id=content_id,
            price=final_price,
            author=author
        )
        
        if not success:
            return False, message
        
        # Enregistrer l'achat
        purchase = ContentPurchase.objects.create(
            user=user,
            content_type=content_type,
            dc_paid=final_price
        )
        
        if content_type == 'course':
            purchase.course_id = content_id
        elif content_type == 'td':
            purchase.td_id = content_id
        elif content_type == 'corrected_td':
            purchase.corrected_td_id = content_id
        
        purchase.save()
        
        if discount > 0:
            return True, f"Contenu acheté avec succès pour {final_price} DC (réduction: {discount} DC)."
        return True, f"Contenu acheté avec succès pour {final_price} DC."
    
    @staticmethod
    def can_access(user, content_type, content_id, price):
        """Vérifie si l'utilisateur peut accéder au contenu."""
        if price == 0:
            return True
        return ContentPurchaseService.has_purchased(user, content_type, content_id)


class ContentVersionService:
    """Service pour gérer le versioning du contenu."""
    
    @staticmethod
    @transaction.atomic
    def create_version(content, change_summary, user):
        """
        Crée une nouvelle version du contenu.
        
        Args:
            content: L'objet Course, TD ou CorrectedTD
            change_summary: Description des changements
            user: L'utilisateur qui fait la modification
            
        Returns:
            ContentVersion: La nouvelle version créée
        """
        # Déterminer le type de contenu
        if isinstance(content, Course):
            content_type = 'course'
            content_id = content.id
        elif isinstance(content, TD):
            content_type = 'td'
            content_id = content.id
        elif isinstance(content, CorrectedTD):
            content_type = 'corrected_td'
            content_id = content.id
        else:
            raise ValueError("Type de contenu non supporté")
        
        # Incrémenter le numéro de version
        current_version = content.current_version
        new_version = current_version + 1
        
        # Créer la nouvelle version
        version = ContentVersion.objects.create(
            content_type=content_type,
            content_id=content_id,
            version_number=new_version,
            title=content.title,
            description=content.description if hasattr(content, 'description') else '',
            content=content.content if hasattr(content, 'content') else '',
            content_file=content.content_file if hasattr(content, 'content_file') else None,
            change_summary=change_summary,
            created_by=user
        )
        
        # Mettre à jour la version actuelle du contenu
        content.current_version = new_version
        content.save()
        
        return version
    
    @staticmethod
    def get_version_history(content):
        """
        Récupère l'historique des versions d'un contenu.
        
        Args:
            content: L'objet Course, TD ou CorrectedTD
            
        Returns:
            QuerySet: Les versions du contenu
        """
        # Déterminer le type de contenu
        if isinstance(content, Course):
            content_type = 'course'
            content_id = content.id
        elif isinstance(content, TD):
            content_type = 'td'
            content_id = content.id
        elif isinstance(content, CorrectedTD):
            content_type = 'corrected_td'
            content_id = content.id
        else:
            raise ValueError("Type de contenu non supporté")
        
        return ContentVersion.objects.filter(
            content_type=content_type,
            content_id=content_id
        ).order_by('-version_number')
    
    @staticmethod
    def restore_version(content, version_number, user):
        """
        Restaure une version précédente du contenu.
        
        Args:
            content: L'objet Course, TD ou CorrectedTD
            version_number: Le numéro de version à restaurer
            user: L'utilisateur qui fait la restauration
            
        Returns:
            ContentVersion: La nouvelle version créée après restauration
        """
        # Récupérer la version à restaurer
        # Déterminer le type de contenu
        if isinstance(content, Course):
            content_type = 'course'
            content_id = content.id
        elif isinstance(content, TD):
            content_type = 'td'
            content_id = content.id
        elif isinstance(content, CorrectedTD):
            content_type = 'corrected_td'
            content_id = content.id
        else:
            raise ValueError("Type de contenu non supporté")
        
        version_to_restore = ContentVersion.objects.get(
            content_type=content_type,
            content_id=content_id,
            version_number=version_number
        )
        
        # Restaurer le contenu
        content.title = version_to_restore.title
        if hasattr(content, 'description'):
            content.description = version_to_restore.description
        if hasattr(content, 'content'):
            content.content = version_to_restore.content
        if hasattr(content, 'content_file'):
            content.content_file = version_to_restore.content_file
        
        # Créer une nouvelle version avec le contenu restauré
        return ContentVersionService.create_version(
            content=content,
            change_summary=f"Restauration de la version {version_number}",
            user=user
        )
