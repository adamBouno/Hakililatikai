from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    telephone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    adresse = models.TextField(blank=True, verbose_name="Adresse")
    date_naissance = models.DateField(null=True, blank=True, verbose_name="Date de naissance")
    genre = models.CharField(max_length=10, choices=[
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ], blank=True, verbose_name="Genre")
    groupe_sanguin = models.CharField(max_length=5, blank=True, verbose_name="Groupe sanguin")
    allergies = models.TextField(blank=True, verbose_name="Allergies connues")
    antecedents = models.TextField(blank=True, verbose_name="Antécédents médicaux")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profil Utilisateur"
        verbose_name_plural = "Profils Utilisateurs"

    def __str__(self):
        return f"Profil de {self.user.username}"

# Signal pour créer automatiquement un profil quand un utilisateur est créé
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        # Si le profil n'existe pas, le créer
        Profile.objects.create(user=instance)

class Recherche(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recherches")
    audio = models.FileField(upload_to="symptomes/", blank=True, null=True)
    symptomes_bam = models.TextField(verbose_name="Symptômes (Bambara)", default="Aucun symptôme")
    symptomes_fr = models.TextField(verbose_name="Symptômes (Français)", blank=True)
    reponse_bam = models.TextField(verbose_name="Réponse (Bambara)", blank=True)
    reponse_mp3 = models.FileField(upload_to="reponses/", blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name = "Recherche Médicale"
        verbose_name_plural = "Recherches Médicales"

    def __str__(self):
        return f"{self.user.username} - {self.date:%Y-%m-%d %H:%M}"

class Rappel(models.Model):
    

    PERIODICITE_CHOICES = [
        ('PONCTUEL', 'Ponctuel'),
        ('QUOTIDIEN', 'Quotidien'),
        ('HEBDOMADAIRE', 'Hebdomadaire'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rappels")
    titre = models.CharField(max_length=200, default="Rappel médical")
    description = models.TextField(blank=True)
    heure = models.TimeField()
    periodique = models.CharField(max_length=20, choices=PERIODICITE_CHOICES, default='PONCTUEL')
    actif = models.BooleanField(default=True)
    medicament = models.CharField(max_length=200, blank=True)
    class Meta:
        ordering = ['heure']
        verbose_name = "Rappel Médical"
        verbose_name_plural = "Rappels Médicaux"

    def __str__(self):
        return f"{self.titre} - {self.get_periodique_display()}"

class CentreMedical(models.Model):
    TYPE_CHOICES = [
        ('CS', 'Centre de Santé'),
        ('HP', 'Hôpital'),
        ('PS', 'Poste de Santé'),
    ]
    
    nom = models.CharField(max_length=200)
    type = models.CharField(max_length=2, choices=TYPE_CHOICES)
    adresse = models.TextField()
    telephone = models.CharField(max_length=20, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    services = models.TextField(blank=True, help_text="Services offerts, séparés par des virgules")

    class Meta:
        ordering = ['nom']
        verbose_name = "Centre Médical"
        verbose_name_plural = "Centres Médicaux"

    def __str__(self):
        return f"{self.get_type_display()} - {self.nom}"

class Article(models.Model):
    CATEGORIE_CHOICES = [
        ('PREV', 'Prévention'),
        ('SYMP', 'Symptômes'),
        ('TRAIT', 'Traitement'),
        ('URG', 'Urgence'),
    ]
    
    titre = models.CharField(max_length=200)
    categorie = models.CharField(max_length=5, choices=CATEGORIE_CHOICES)
    contenu = models.TextField()
    date_publication = models.DateField(auto_now_add=True)
    image = models.ImageField(upload_to='articles/')
    auteur = models.CharField(max_length=100, blank=True)
    mots_cles = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-date_publication']
        verbose_name = "Article de Santé"
        verbose_name_plural = "Articles de Santé"

    def __str__(self):
        return self.titre

    def get_extrait(self, length=200):
        return self.contenu[:length] + '...' if len(self.contenu) > length else self.contenu