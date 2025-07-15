from django.urls import path
from rest_framework import viewsets
from . import views
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from rest_framework import routers
from .views import RechercheViewSet,RappelViewSet  #
from .views import SignUpView, login_view, home, reminders
from .views import (
    TranscriptionAPIView,
    TraductionAPIView,
    TTSAPIView,
)
from . import views_test

urlpatterns = [
    path("transcribe/", TranscriptionAPIView.as_view(), name="api-transcribe"),
    path("translate/",  TraductionAPIView.as_view(),name="api-translate"),
    path("tts/", TTSAPIView.as_view(), name="api-tts"),
    path("", views.home, name="home"),
    path("profile/", views.profile, name="profile"),
    path("rappels/", views.reminders, name="reminders"),
    path("login/",  views.login_view, name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="home", http_method_names=['get', 'post']), name="logout"),
    path("signup/", views.signup, name="signup"), 
    path('centres/', views.centres_medicaux, name='centres'),
    path('apropos/', TemplateView.as_view(template_name='core/about.html'), name='about'),
    path('articles/', views.articles, name='articles'),
    path('symptomes/', views.pipeline, name='pipeline'),
    
    # URLs pour les tests Colab
    path('test-colab/', views_test.test_colab_interface, name='test-colab'),
    path('test-transcription-api/', views_test.test_transcription_api, name='test-transcription-api'),
    path('test-colab-health/', views_test.test_colab_health, name='test-colab-health'),
    path('test-batch/', views_test.test_batch_transcription, name='test-batch'),

]

router = DefaultRouter()
router.register("recherches", RechercheViewSet, basename="recherche")
router.register("rappels", RappelViewSet, basename="rappel")

urlpatterns += router.urls

