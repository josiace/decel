"""
Validateurs personnalisés pour l'API DECEL.
Améliore la validation des données entrantes.
"""
import re
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


def validate_referral_code(value):
    """
    Valide le format d'un code de parrainage.
    Format attendu: DECEL-{id}-{username_prefix}
    """
    if not value:
        raise ValidationError("Le code de parrainage est requis.")
    
    pattern = r'^DECEL-\d+-[A-Z0-9]{4}$'
    if not re.match(pattern, value):
        raise ValidationError(
            "Format de code de parrainage invalide. "
            "Format attendu: DECEL-{id}-{4_lettres}"
        )
    return value


def validate_recharge_code(value):
    """
    Valide le format d'un code de recharge.
    """
    if not value:
        raise ValidationError("Le code de recharge est requis.")
    
    if len(value) < 8 or len(value) > 20:
        raise ValidationError(
            "Le code de recharge doit contenir entre 8 et 20 caractères."
        )
    
    if not value.isalnum():
        raise ValidationError(
            "Le code de recharge ne doit contenir que des lettres et chiffres."
        )
    return value


def validate_promo_code(value):
    """
    Valide le format d'un code promo.
    """
    if not value:
        raise ValidationError("Le code promo est requis.")
    
    if len(value) < 3 or len(value) > 30:
        raise ValidationError(
            "Le code promo doit contenir entre 3 et 30 caractères."
        )
    
    return value.upper()


def validate_payment_method(value):
    """
    Valide la méthode de paiement.
    """
    valid_methods = ['stripe', 'orange_money', 'wave', 'bank_transfer', 'cash', 'recharge_code']
    if value not in valid_methods:
        raise ValidationError(
            f"Méthode de paiement invalide. Options valides: {', '.join(valid_methods)}"
        )
    return value


def validate_transaction_reference(value):
    """
    Valide la référence de transaction pour paiements manuels.
    """
    if not value or not value.strip():
        raise ValidationError("La référence de transaction est requise pour les paiements manuels.")
    
    if len(value) > 255:
        raise ValidationError("La référence de transaction ne peut pas dépasser 255 caractères.")
    
    return value.strip()
