from django import template
from django.templatetags.static import static
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def optimized_image(image_path, alt_text="", width=None, height=None, loading="lazy"):
    """
    Génère une balise image optimisée avec lazy loading et attributs modernes.
    
    Args:
        image_path: Chemin de l'image
        alt_text: Texte alternatif pour l'accessibilité
        width: Largeur optionnelle
        height: Hauteur optionnelle
        loading: Type de chargement (lazy, eager, auto)
    """
    image_url = static(image_path)
    
    attrs = {
        'src': image_url,
        'alt': alt_text,
        'loading': loading,
        'decoding': 'async',
    }
    
    if width:
        attrs['width'] = width
    if height:
        attrs['height'] = height
    
    attrs_str = ' '.join([f'{k}="{v}"' for k, v in attrs.items()])
    
    return format_html('<img {} />', attrs_str)


@register.simple_tag
def responsive_image(image_path, alt_text="", sizes="100vw", loading="lazy"):
    """
    Génère une balise image responsive avec srcset pour différentes résolutions.
    
    Args:
        image_path: Chemin de l'image
        alt_text: Texte alternatif
        sizes: Attribut sizes pour le responsive
        loading: Type de chargement
    """
    image_url = static(image_path)
    
    # Simuler différentes résolutions (en production, utiliser des images réelles)
    srcset = f"{image_url} 1x, {image_url} 2x"
    
    attrs = {
        'src': image_url,
        'srcset': srcset,
        'alt': alt_text,
        'loading': loading,
        'decoding': 'async',
        'sizes': sizes,
    }
    
    attrs_str = ' '.join([f'{k}="{v}"' for k, v in attrs.items()])
    
    return format_html('<img {} />', attrs_str)
