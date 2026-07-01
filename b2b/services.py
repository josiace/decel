from django.db import transaction
from django.utils import timezone
from datetime import timedelta
import secrets
from .models import B2BPartner, B2BLicense, B2BUser, B2BTransaction


class B2BService:
    """Service pour gérer les partenariats et licences B2B."""
    
    @staticmethod
    @transaction.atomic
    def create_partner(partner_data):
        """
        Crée un nouveau partenaire B2B.
        
        Args:
            partner_data: Données du partenaire
            
        Returns:
            B2BPartner: Le partenaire créé
        """
        partner = B2BPartner.objects.create(**partner_data)
        return partner
    
    @staticmethod
    @transaction.atomic
    def create_license(partner_id, license_data):
        """
        Crée une nouvelle licence B2B.
        
        Args:
            partner_id: ID du partenaire
            license_data: Données de la licence
            
        Returns:
            B2BLicense: La licence créée
        """
        partner = B2BPartner.objects.get(id=partner_id)
        
        # Générer une clé de licence unique
        license_key = B2BService.generate_license_key()
        
        license = B2BLicense.objects.create(
            partner=partner,
            license_key=license_key,
            **license_data
        )
        
        return license
    
    @staticmethod
    def generate_license_key():
        """Génère une clé de licence unique."""
        while True:
            license_key = secrets.token_urlsafe(32)
            if not B2BLicense.objects.filter(license_key=license_key).exists():
                return license_key
    
    @staticmethod
    @transaction.atomic
    def add_user_to_license(license_id, user_id, role, added_by):
        """
        Ajoute un utilisateur à une licence.
        
        Args:
            license_id: ID de la licence
            user_id: ID de l'utilisateur
            role: Rôle de l'utilisateur
            added_by: Utilisateur qui ajoute
            
        Returns:
            tuple: (success: bool, message: str, b2b_user: B2BUser or None)
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        license = B2BLicense.objects.get(id=license_id)
        user = User.objects.get(id=user_id)
        
        # Vérifier les limites
        if role == 'student':
            if license.current_students >= license.max_students:
                return False, "Limite d'étudiants atteinte.", None
        elif role == 'teacher':
            if license.current_teachers >= license.max_teachers:
                return False, "Limite d'enseignants atteinte.", None
        
        # Vérifier si l'utilisateur est déjà dans la licence
        if B2BUser.objects.filter(license=license, user=user).exists():
            return False, "L'utilisateur est déjà dans cette licence.", None
        
        # Créer l'association
        b2b_user = B2BUser.objects.create(
            license=license,
            user=user,
            role=role,
            added_by=added_by
        )
        
        # Mettre à jour les compteurs
        if role == 'student':
            license.current_students += 1
        elif role == 'teacher':
            license.current_teachers += 1
        license.save()
        
        return True, "Utilisateur ajouté avec succès.", b2b_user
    
    @staticmethod
    @transaction.atomic
    def remove_user_from_license(license_id, user_id):
        """
        Retire un utilisateur d'une licence.
        
        Args:
            license_id: ID de la licence
            user_id: ID de l'utilisateur
            
        Returns:
            tuple: (success: bool, message: str)
        """
        license = B2BLicense.objects.get(id=license_id)
        b2b_user = B2BUser.objects.get(license=license, user_id=user_id)
        
        role = b2b_user.role
        
        # Mettre à jour les compteurs
        if role == 'student':
            license.current_students -= 1
        elif role == 'teacher':
            license.current_teachers -= 1
        license.save()
        
        # Supprimer l'association
        b2b_user.delete()
        
        return True, "Utilisateur retiré avec succès."
    
    @staticmethod
    @transaction.atomic
    def renew_license(license_id, new_end_date):
        """
        Renouvelle une licence.
        
        Args:
            license_id: ID de la licence
            new_end_date: Nouvelle date de fin
            
        Returns:
            tuple: (success: bool, message: str)
        """
        license = B2BLicense.objects.get(id=license_id)
        
        if not license.is_active():
            return False, "Cette licence n'est pas active."
        
        license.end_date = new_end_date
        license.save()
        
        # Créer une transaction de renouvellement
        B2BTransaction.objects.create(
            partner=license.partner,
            license=license,
            transaction_type='license_renewal',
            amount_cfa=license.price_cfa,
            status='pending'
        )
        
        return True, "Licence renouvelée avec succès."
    
    @staticmethod
    @transaction.atomic
    def upgrade_license(license_id, additional_seats):
        """
        Upgrade une licence avec des places supplémentaires.
        
        Args:
            license_id: ID de la licence
            additional_seats: Nombre de places supplémentaires
            
        Returns:
            tuple: (success: bool, message: str)
        """
        license = B2BLicense.objects.get(id=license_id)
        
        license.max_students += additional_seats
        license.save()
        
        # Créer une transaction d'upgrade
        price_per_seat = license.price_cfa / license.max_students
        additional_cost = price_per_seat * additional_seats
        
        B2BTransaction.objects.create(
            partner=license.partner,
            license=license,
            transaction_type='add_seats',
            amount_cfa=additional_cost,
            status='pending'
        )
        
        return True, f"Licence upgrade avec {additional_seats} places supplémentaires."
    
    @staticmethod
    @transaction.atomic
    def complete_transaction(transaction_id, payment_reference=""):
        """
        Marque une transaction comme complétée.
        
        Args:
            transaction_id: ID de la transaction
            payment_reference: Référence de paiement
            
        Returns:
            tuple: (success: bool, message: str)
        """
        transaction = B2BTransaction.objects.get(id=transaction_id)
        
        transaction.status = 'completed'
        transaction.payment_reference = payment_reference
        transaction.completed_at = timezone.now()
        transaction.save()
        
        return True, "Transaction complétée avec succès."
    
    @staticmethod
    def get_partner_licenses(partner_id, status='active'):
        """
        Récupère les licences d'un partenaire.
        
        Args:
            partner_id: ID du partenaire
            status: Statut des licences (optionnel)
            
        Returns:
            QuerySet: Licences du partenaire
        """
        licenses = B2BLicense.objects.filter(partner_id=partner_id)
        if status:
            licenses = licenses.filter(status=status)
        return licenses
    
    @staticmethod
    def get_license_users(license_id, role=None):
        """
        Récupère les utilisateurs d'une licence.
        
        Args:
            license_id: ID de la licence
            role: Rôle des utilisateurs (optionnel)
            
        Returns:
            QuerySet: Utilisateurs de la licence
        """
        users = B2BUser.objects.filter(license_id=license_id)
        if role:
            users = users.filter(role=role)
        return users.select_related('user')
    
    @staticmethod
    def get_user_license(user_id):
        """
        Récupère la licence d'un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            B2BLicense or None
        """
        b2b_user = B2BUser.objects.filter(user_id=user_id).first()
        if b2b_user:
            return b2b_user.license
        return None
    
    @staticmethod
    def check_license_limits(license_id):
        """
        Vérifie les limites d'une licence.
        
        Args:
            license_id: ID de la licence
            
        Returns:
            dict: Statistiques d'utilisation
        """
        license = B2BLicense.objects.get(id=license_id)
        
        return {
            'max_students': license.max_students,
            'current_students': license.current_students,
            'students_remaining': license.max_students - license.current_students,
            'students_usage_percentage': license.usage_percentage(),
            'max_teachers': license.max_teachers,
            'current_teachers': license.current_teachers,
            'teachers_remaining': license.max_teachers - license.current_teachers,
            'is_active': license.is_active(),
            'days_remaining': license.days_remaining(),
        }
