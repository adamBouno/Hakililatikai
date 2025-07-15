from rest_framework import serializers
from .models import Recherche, Rappel, CentreMedical, Article
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class RechercheSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    audio_url = serializers.SerializerMethodField()
    reponse_mp3_url = serializers.SerializerMethodField()

    class Meta:
        model = Recherche
        fields = [
            'id', 'user', 'date',
            'audio_url', 'symptomes_bam', 'symptomes_fr',
            'reponse_bam', 'reponse_mp3_url'
        ]
        read_only_fields = fields

    def get_audio_url(self, obj):
        if obj.audio:
            return obj.audio.url
        return None

    def get_reponse_mp3_url(self, obj):
        if obj.reponse_mp3:
            return obj.reponse_mp3.url
        return None

class RappelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rappel
        fields = ['id', 'titre', 'description', 'heure', 'periodique', 'actif']
        extra_kwargs = {
            'user': {'write_only': True}
        }

class CentreMedicalSerializer(serializers.ModelSerializer):
    distance = serializers.SerializerMethodField()

    class Meta:
        model = CentreMedical
        fields = [
            'id', 'nom', 'type', 'adresse', 'telephone',
            'latitude', 'longitude', 'services', 'distance'
        ]

    def get_distance(self, obj):
        request = self.context.get('request')
        if request and hasattr(obj, 'distance'):
            return obj.distance
        return None

class ArticleSerializer(serializers.ModelSerializer):
    extrait = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'titre', 'categorie', 'extrait',
            'date_publication', 'image_url', 'auteur'
        ]

    def get_extrait(self, obj):
        return obj.get_extrait()

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None