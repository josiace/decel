from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import cache_page
from .models import BlogPost, BlogCategory


@cache_page(60 * 15)  # 15 minutes
def blog_home(request):
    """Page d'accueil du blog avec tous les articles publiés."""
    posts = BlogPost.objects.filter(status='published').select_related('author')
    categories = BlogCategory.objects.all()
    
    context = {
        'posts': posts,
        'categories': categories,
        'meta_description': 'Blog DECEL - Articles sur l\'apprentissage adaptatif, l\'éducation en Afrique francophone, les conseils pour réussir vos examens et bien plus.',
    }
    return render(request, 'blog/blog_home.html', context)


def post_detail(request, slug):
    """Page de détail d'un article de blog."""
    post = get_object_or_404(BlogPost, slug=slug, status='published')
    
    # Incrémenter le compteur de vues
    post.views_count += 1
    post.save(update_fields=['views_count'])
    
    context = {
        'post': post,
        'meta_description': post.meta_description or post.excerpt or post.content[:160],
    }
    return render(request, 'blog/post_detail.html', context)


def category_posts(request, category_slug):
    """Articles filtrés par catégorie."""
    category = get_object_or_404(BlogCategory, slug=category_slug)
    posts = BlogPost.objects.filter(status='published').select_related('author')
    
    context = {
        'category': category,
        'posts': posts,
        'meta_description': f'Articles sur {category.name} - Blog DECEL. {category.description[:100] if category.description else ""}',
    }
    return render(request, 'blog/category_posts.html', context)
