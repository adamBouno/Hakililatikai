from django.contrib import admin
from .models import Recherche, Rappel, CentreMedical, Article, Profile

@admin.register(CentreMedical)
class CentreMedicalAdmin(admin.ModelAdmin):
    list_display = ('nom', 'type', 'adresse', 'telephone', 'latitude', 'longitude')
    list_filter = ('type',)
    search_fields = ('nom', 'adresse', 'services')
    list_per_page = 20
    ordering = ('nom',)
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'type', 'adresse', 'telephone')
        }),
        ('Coordonnées GPS', {
            'fields': ('latitude', 'longitude'),
            'description': 'Coordonnées GPS pour la géolocalisation'
        }),
        ('Services', {
            'fields': ('services',),
            'description': 'Liste des services proposés par ce centre'
        }),
    )

admin.site.register(Recherche)
admin.site.register(Rappel)
admin.site.register(Article)
admin.site.register(Profile)
 