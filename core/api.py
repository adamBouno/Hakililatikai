from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import HttpResponse
from .models import Recherche, Rappel, CentreMedical, Article
from .serializers import (RechercheSerializer, RappelSerializer,
                         CentreMedicalSerializer, ArticleSerializer)
from .utils import recherche_pipeline
# from django.contrib.gis.geos import Point
# from django.contrib.gis.db.models.functions import Distance
# from django.contrib.gis.measure import D
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from django.urls import path, include
from rest_framework.routers import DefaultRouter

User = get_user_model()

class RechercheMedicaleAPI(APIView):
    """
    Endpoint pour le pipeline complet de recherche médicale
    Accepte soit du texte soit un fichier audio
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        # Vérifie si c'est un fichier audio ou du texte
        audio_file = request.FILES.get('audio')
        text_input = request.data.get('text', '').strip()
        
        if audio_file:
            result = recherche_pipeline(audio_file, request.user, is_audio=True)
        elif text_input:
            result = recherche_pipeline(text_input, request.user, is_audio=False)
        else:
            return Response(
                {"error": "Fournir soit un fichier audio soit du texte"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not result['success']:
            return Response(
                {"error": result['error']},
                status=status.HTTP_502_BAD_GATEWAY
            )
        
        return Response(result, status=status.HTTP_200_OK)

class RappelViewSet(viewsets.ModelViewSet):
    serializer_class = RappelSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Rappel.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CentreMedicalViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CentreMedicalSerializer
    queryset = CentreMedical.objects.all()
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Fonctionnalité géospatiale temporairement désactivée
        # lat = self.request.query_params.get('lat')
        # lng = self.request.query_params.get('lng')
        
        # if lat and lng:
        #     try:
        #         point = Point(float(lng), float(lat), srid=4326)
        #         queryset = queryset.annotate(
        #             distance=Distance('location', point)
        #     ).order_by('distance')[:10]
        #     except (ValueError, TypeError):
        #         pass
        return queryset

class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()
    
    def get_queryset(self):
        queryset = super().get_queryset()
        categorie = self.request.query_params.get('categorie')
        
        if categorie:
            queryset = queryset.filter(categorie=categorie)
        return queryset.order_by('-date_publication')[:20]
    
class AuthAPI(APIView):
    """
    Gestion de l'authentification pour obtenir le token
    
    Exemple :
    POST /api/auth/ - Obtenir un token avec username/password
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response(
                {"error": "Username et password requis"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = User.objects.filter(username=username).first()
        if not user or not user.check_password(password):
            return Response(
                {"error": "Identifiants invalides"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "user_id": user.id,
            "username": user.username
        })

# Configuration des URLs pour l'API
router = DefaultRouter()
router.register(r'rappels', RappelViewSet, basename='rappel')
router.register(r'centres', CentreMedicalViewSet, basename='centre')
router.register(r'articles', ArticleViewSet, basename='article')

urlpatterns = [
    path('recherche/', RechercheMedicaleAPI.as_view(), name='recherche'),
    path('auth/', AuthAPI.as_view(), name='auth'),
    path('', include(router.urls)),
]