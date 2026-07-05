from django.contrib import admin
from .models import BlogPost, BlogCategory


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'created_at', 'published_at', 'views_count')
    list_filter = ('status', 'category', 'created_at', 'published_at')
    search_fields = ('title', 'content', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'views_count')
    date_hierarchy = 'published_at'

    fieldsets = (
        ('Informations principales', {
            'fields': ('title', 'slug', 'author', 'category', 'status')
        }),
        ('Contenu', {
            'fields': ('content', 'excerpt', 'featured_image')
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords')
        }),
        ('Statistiques', {
            'fields': ('views_count', 'created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )
