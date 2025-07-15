from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status, permissions,viewsets
from django.http import HttpResponse
from .utils import transcrire, traduire, synthese
from .forms import SignUpForm
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .serializers import RechercheSerializer,RappelSerializer
from .forms import RappelForm
from .models import Rappel,Recherche,Article,CentreMedical
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth import login as auth_login
import math
from .utils import transcrire, traduire, synthese, duckduck_medical_search,recherche_pipeline
from .utils_colab import recherche_pipeline_colab
import uuid
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.base import ContentFile
from django.http import JsonResponse
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Article, CentreMedical, Rappel
from .forms import MedicalSignUpForm, MedicalLoginForm, SignUpForm, RappelForm
import json
from functools import wraps

logger = logging.getLogger(__name__)

def require_login(view_func):
    """Décorateur pour rediriger vers la connexion si l'utilisateur n'est pas connecté"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Veuillez vous connecter pour accéder à cette page.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

class TranscriptionAPIView(APIView):
   # permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser]  # pour gérer les fichiers
    def post(self, request, format=None):
        audio_file = request.FILES.get("file")
        if not audio_file:
            return Response({"detail": "Pas de fichier audio."},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            texte = transcrire(audio_file.read())
            return Response({"text": texte})
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

class TraductionAPIView(APIView):
   # permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        text = request.data.get("text")
        direction = request.data.get("direction", "bam-fra")
        if not text:
            return Response({"detail": "Pas de texte à traduire."},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            trad = traduire(text, direction)
            return Response({"translation": trad})
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

class TTSAPIView(APIView):
   # permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        text = request.data.get("text")
        if not text:
            return Response({"detail": "Pas de texte pour synthèse."},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            audio_bytes = synthese(text)
            return HttpResponse(audio_bytes, content_type="audio/mpeg")
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

@login_required
def reminders(request):
    if request.GET.get('historique') == '1':
        recherches = request.user.recherches.order_by('-date')[:20]
        return render(request, "core/historique.html", {"recherches": recherches})
    form = RappelForm(request.POST or None)
    if form.is_valid():
        rappel = form.save(commit=False)
        rappel.user = request.user
        rappel.save()
        return redirect("reminders")
    rappels = Rappel.objects.filter(user=request.user).order_by("-heure")
    return render(request, "core/reminders.html", {"form": form, "rappels": rappels})

def home(request):
    slide_images = [f"slide{i}.png" for i in range(1, 10)]   
    
    # Récupérer les articles depuis la base de données
    articles = Article.objects.all().order_by('-date_publication')[:8]
    
    # Transformer les objets Article en format compatible avec le template
    articles_data = []
    for article in articles:
        articles_data.append({
            "titre": article.titre,
            "accroche": article.get_extrait(100),  # Utilise la méthode get_extrait du modèle
            "img": article.image,  # Utilise l'image de l'article de la base de données
            "id": article.id,  # Ajoute l'ID pour les liens
            "categorie": article.categorie
        })
    
    # Si pas assez d'articles en base, compléter avec des données par défaut
    default_articles = [
        {"titre": "Prévenir le paludisme", "accroche": "Conseils de prévention…", "img": "carte1.png"},
        {"titre": "Reconnaître l’anémie", "accroche": "Signes et premiers gestes", "img": "carte2.png"},
        {"titre": "Fièvre chez l’enfant", "accroche": "Quand consulter rapidement ?", "img": "carte3.png"},
        {"titre": "Vaccinations essentielles", "accroche": "Le calendrier simplifié", "img": "carte4.png"},
        {"titre": "Diabète : surveiller sa glycémie", "accroche": "Mesures quotidiennes faciles", "img": "carte5.png"},
        {"titre": "Hypertension : bons réflexes", "accroche": "Sel, sport et suivi régulier", "img": "carte6.png"},
        {"titre": "Grossesse : signaux d’alerte", "accroche": "Quand aller au centre ?", "img": "carte7.png"},
        {"titre": "Déshydratation : réagir vite", "accroche": "ORS maison en 3 étapes", "img": "carte8.png"},
    ]
    while len(articles_data) < 8:
        articles_data.append(default_articles[len(articles_data)])
    
    return render(request, "core/home.html", {"slide_images": slide_images, "articles": articles_data})

@login_required
def profile(request):
    recherches = request.user.recherches.order_by('-date')[:20]
    return render(request, "core/profile.html", {"recherches": recherches})

def signup(request):
    """Vue d'inscription avec formulaire médical personnalisé"""
    if request.method == 'POST':
        form = MedicalSignUpForm(request.POST)
        if form.is_valid():
            try:
                # Sauvegarder l'utilisateur directement avec le formulaire
                user = form.save()
                
                # Connecter automatiquement l'utilisateur
                login(request, user)
                messages.success(request, 'Compte créé avec succès ! Bienvenue sur Rassurez-moi.')
                return redirect('home')
            except Exception as e:
                # En cas d'erreur, afficher un message d'erreur plus détaillé
                error_msg = f'Erreur lors de la création du compte. '
                if 'Duplicate entry' in str(e):
                    error_msg += 'Ce nom d\'utilisateur existe déjà.'
                elif 'IntegrityError' in str(e):
                    error_msg += 'Problème avec la base de données. Veuillez réessayer.'
                else:
                    error_msg += str(e)
                
                messages.error(request, error_msg)
                return render(request, "core/signup.html", {"form": form})
    else:
        form = MedicalSignUpForm()
    
    return render(request, "core/signup.html", {"form": form})

def login_view(request):
    """Vue de connexion avec formulaire médical personnalisé"""
    if request.method == 'POST':
        form = MedicalLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)
            
            # Essayer de s'authentifier avec le nom d'utilisateur ou l'email
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                if not remember_me:
                    # Définir la session pour expirer à la fermeture du navigateur
                    request.session.set_expiry(0)
                
                messages.success(request, f'Bienvenue {user.username} !')
                return redirect('home')
            else:
                messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    else:
        form = MedicalLoginForm()
    
    return render(request, "registration/login.html", {"form": form})

class RechercheViewSet(viewsets.ModelViewSet):
    queryset = Recherche.objects.all()
    serializer_class = RechercheSerializer
class RappelViewSet(viewsets.ModelViewSet):
    queryset         = Rappel.objects.all()
    serializer_class = RappelSerializer

def haversine(lat1, lon1, lat2, lon2):
    # Rayon de la Terre en km
    R = 6371  
    φ1, φ2 = math.radians(lat1), math.radians(lat2)
    Δφ = math.radians(lat2 - lat1)
    Δλ = math.radians(lon2 - lon1)
    a = math.sin(Δφ/2)**2 + math.cos(φ1)*math.cos(φ2)*math.sin(Δλ/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

@require_login
def centres_medicaux(request):
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    
    # Ajout automatique des centres par défaut (force l'ajout pour tester)
    if CentreMedical.objects.count() < 5:  # Si moins de 5 centres, on ajoute la liste complète
        CentreMedical.objects.bulk_create([
            # Hôpitaux (HP)
            CentreMedical(nom="Hôpital du Point G", type="HP", adresse="Bamako, Point G", telephone="+223 20 22 37 37", latitude=12.6300, longitude=-7.9900, services="Hôpital universitaire, Urgences, Chirurgie, Maternité, Pédiatrie"),
            CentreMedical(nom="Hôpital Gabriel Touré", type="HP", adresse="Bamako, Hamdallaye ACI", telephone="+223 20 22 37 37", latitude=12.6512, longitude=-8.0123, services="Urgences, Consultations, Laboratoire, Imagerie"),
            CentreMedical(nom="Hôpital Mère-Enfant", type="HP", adresse="Bamako, Faladié", telephone="+223 20 22 37 37", latitude=12.6450, longitude=-7.9850, services="Maternité, Pédiatrie, Gynécologie, Urgences"),
            CentreMedical(nom="Hôpital National", type="HP", adresse="Bamako, Quartier du Fleuve", telephone="+223 20 22 37 37", latitude=12.6350, longitude=-7.9950, services="Urgences, Chirurgie, Médecine interne, Spécialités"),
            
            # Cliniques (CL)
            CentreMedical(nom="Clinique Pasteur", type="CL", adresse="Bamako, Hamdallaye ACI", telephone="+223 20 22 37 37", latitude=12.6512, longitude=-8.0123, services="Consultations, Laboratoire, Vaccination, Médecine générale"),
            CentreMedical(nom="Clinique Golden Life", type="CL", adresse="Bamako, ACI 2000", telephone="+223 20 22 37 37", latitude=12.6392, longitude=-8.0029, services="Consultations, Imagerie, Médecine générale, Spécialités"),
            CentreMedical(nom="Clinique Médicale du Mali", type="CL", adresse="Bamako, Badalabougou", telephone="+223 20 22 37 37", latitude=12.6400, longitude=-8.0000, services="Consultations, Laboratoire, Médecine générale"),
            CentreMedical(nom="Clinique Farako", type="CL", adresse="Bamako, Farako", telephone="+223 20 22 37 37", latitude=12.6480, longitude=-8.0080, services="Consultations, Médecine générale, Pédiatrie"),
            CentreMedical(nom="Clinique Médicale de l'ACI", type="CL", adresse="Bamako, ACI 2000", telephone="+223 20 22 37 37", latitude=12.6420, longitude=-8.0050, services="Consultations, Laboratoire, Médecine générale"),
            CentreMedical(nom="Clinique Médicale de Badalabougou", type="CL", adresse="Bamako, Badalabougou", telephone="+223 20 22 37 37", latitude=12.6380, longitude=-7.9980, services="Consultations, Médecine générale, Pédiatrie"),
            
            # Centres d'Urgences (UR)
            CentreMedical(nom="Centre d'Urgences Médicales", type="UR", adresse="Bamako, Centre-ville", telephone="+223 20 22 37 37", latitude=12.6500, longitude=-8.0000, services="Urgences 24/7, SAMU, Réanimation"),
            CentreMedical(nom="Centre d'Urgences de l'ACI", type="UR", adresse="Bamako, ACI 2000", telephone="+223 20 22 37 37", latitude=12.6410, longitude=-8.0030, services="Urgences, Ambulance, Premiers soins"),
            CentreMedical(nom="Centre d'Urgences de Hamdallaye", type="UR", adresse="Bamako, Hamdallaye", telephone="+223 20 22 37 37", latitude=12.6520, longitude=-8.0130, services="Urgences, SAMU, Réanimation"),
            CentreMedical(nom="Centre d'Urgences de Faladié", type="UR", adresse="Bamako, Faladié", telephone="+223 20 22 37 37", latitude=12.6460, longitude=-7.9860, services="Urgences, Ambulance, Premiers soins"),
            CentreMedical(nom="Centre d'Urgences de Badalabougou", type="UR", adresse="Bamako, Badalabougou", telephone="+223 20 22 37 37", latitude=12.6390, longitude=-7.9970, services="Urgences, SAMU, Réanimation"),
            
            # Centres médicaux supplémentaires
            CentreMedical(nom="Centre Médical de Sotuba", type="CL", adresse="Bamako, Sotuba", telephone="+223 20 22 37 37", latitude=12.6550, longitude=-7.9750, services="Consultations, Médecine générale, Pédiatrie"),
            CentreMedical(nom="Centre Médical de Kalaban", type="CL", adresse="Bamako, Kalaban", telephone="+223 20 22 37 37", latitude=12.6600, longitude=-7.9700, services="Consultations, Médecine générale"),
            CentreMedical(nom="Centre Médical de Niamakoro", type="CL", adresse="Bamako, Niamakoro", telephone="+223 20 22 37 37", latitude=12.6450, longitude=-7.9750, services="Consultations, Médecine générale, Pédiatrie"),
            CentreMedical(nom="Centre Médical de Lafiabougou", type="CL", adresse="Bamako, Lafiabougou", telephone="+223 20 22 37 37", latitude=12.6350, longitude=-7.9800, services="Consultations, Médecine générale"),
            CentreMedical(nom="Centre Médical de Médina", type="CL", adresse="Bamako, Médina", telephone="+223 20 22 37 37", latitude=12.6500, longitude=-7.9900, services="Consultations, Médecine générale, Pédiatrie"),
        ])
    
    centres = list(CentreMedical.objects.all())
    nearest = None
    user_location = None

    if lat and lon:
        lat, lon = float(lat), float(lon)
        user_location = {'lat': lat, 'lon': lon}
        
        # Calcule distance pour chaque centre
        for centre in centres:
            centre.distance = haversine(lat, lon, centre.latitude, centre.longitude)
        
        # Trie les centres par distance (le plus proche en premier)
        centres.sort(key=lambda c: c.distance)
        
        # Le premier est le plus proche
        nearest = centres[0] if centres else None
        
        # Marque le centre le plus proche
        if nearest:
            nearest.is_nearest = True

    return render(request, 'core/centres.html', {
        'nearest': nearest,
        'all_centres': centres,
        'user_location': user_location
    })
def about(request):
    return render(request, "core/about.html")

@require_login
def articles(request):
    """Vue pour afficher tous les articles de la base de données"""
    articles = Article.objects.all().order_by('-date_publication')
    
    # Préparer les extraits pour éviter l'appel de méthode dans le template
    for article in articles:
        article.extrait_150 = article.get_extrait(150)
    
    return render(request, "core/articles.html", {"articles": articles})

@require_login
def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    return render(request, "core/article_detail.html", {"article": article})


class SignUpView(CreateView):
    template_name = "core/registration/signup.html"
    form_class = SignUpForm
    success_url = reverse_lazy("home")  # Redirection vers la page d'accueil

    def form_valid(self, form):
        # Sauvegarde l'utilisateur ET le connecte automatiquement
        user = form.save()
        login(self.request, user)
        return redirect(self.get_success_url())
@require_login
def pipeline(request):
    """
    Vue qui traite la saisie (texte ou audio), appelle le pipeline
    et enregistre l'historique de recherche.
    """
    if request.method == "POST":
        symptomes_bam = request.POST.get("symptomes_bam", "").strip()
        audio_file = request.FILES.get("audio")
        
        if not symptomes_bam and not audio_file:
            return JsonResponse({
                "success": False,
                "error": "Veuillez fournir du texte ou un fichier audio."
            }, status=400)

        try:
            # Utiliser le pipeline Colab pour le traitement audio
            from django.conf import settings
            
            if audio_file:
                # Traitement audio avec Colab
                if hasattr(settings, 'COLAB_NOTEBOOK_URL') and settings.COLAB_NOTEBOOK_URL:
                    result = recherche_pipeline_colab(audio_file, request.user, is_audio=True)
                else:
                    # Fallback vers le pipeline local
                    from .utils import recherche_pipeline
                    result = recherche_pipeline(audio_file, request.user, is_audio=True)
            else:
                # Traitement texte (utilise le pipeline local)
                from .utils import recherche_pipeline
                result = recherche_pipeline(symptomes_bam, request.user, is_audio=False)
            
            if result["success"]:
                return JsonResponse({
                    "success": True,
                    "symptomes_bam": result["symptomes_bam"],
                    "symptomes_fr": result["symptomes_fr"],
                    "reponse_bam": result["reponse_bam"],
                    "audio_url": result.get("audio_url"),
                    "recherche_id": result.get("recherche_id")
                })
            else:
                return JsonResponse({
                    "success": False,
                    "error": result["error"],
                    "reponse_bam": result["reponse_bam"]
                }, status=400)
                
        except Exception as e:
            logger.error(f"Erreur dans la vue pipeline: {str(e)}")
            return JsonResponse({
                "success": False,
                "error": "Une erreur est survenue lors du traitement.",
                "reponse_bam": "Veuillez réessayer plus tard."
            }, status=500)

    # Méthode GET : on affiche le formulaire
    return render(request, "core/pipeline_form.html")
class RechercheAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser]

    def post(self, request):
        audio = request.FILES.get("audio")
        text  = request.data.get("text", "").strip()

        if not audio and not text:
            return Response({"detail": "Aucun audio ni texte."}, status=400)

        # --- ASR ----------------------------------------------------------
        symptomes = text
        if audio:
            symptomes = transcrire(audio.read())

        # --- Recherche / traduction --------------------------------------
        sympt_fr   = traduire(symptomes, "bam-fra")
        conseils_fr = duckduck_medical_search(sympt_fr)   # <-— fallback
        reponse_bam = traduire(conseils_fr, "fra-bam")

        # --- TTS ----------------------------------------------------------
        audio_mp3_bytes = synthese(reponse_bam)          # bytes or None

        # --- BDD ----------------------------------------------------------
        recherche = Recherche.objects.create(
            user        = request.user,
            audio       = audio,
            symptomes   = symptomes,
            reponse_txt = reponse_bam
        )
        if audio_mp3_bytes:
            fname = f"reponses/{uuid.uuid4()}.mp3"
            recherche.reponse_mp3.save(fname,
                                       ContentFile(audio_mp3_bytes))
            recherche.save()

        return Response({
            "id"     : recherche.id,
            "sympt"  : symptomes,
            "reponse": reponse_bam,
            "mp3"    : recherche.reponse_mp3.url if audio_mp3_bytes else None
        }, status=201)
    
    # views.py


def recherche_pipeline(sympt_bam: str, user):
    sympt_fr    = traduire(sympt_bam, "bam-fra")
    conseils_fr = duckduck_medical_search(sympt_fr)   # <-— fallback
    rep_bam     = traduire(conseils_fr, "fra-bam")
    audio_bytes = synthese(rep_bam)
    # Historique
    Recherche.objects.create(user=user, texte=sympt_bam)
    return rep_bam, audio_bytes

# Les signaux sont définis dans models.py, pas besoin de les redéfinir ici
