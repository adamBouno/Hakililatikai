import requests
import json
from django.conf import settings
import re
import html
from urllib.parse import quote_plus
from requests.exceptions import RequestException
import logging
import tempfile
import os
from typing import Union
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

# Configuration API Djelia - À configurer dans settings.py
DJELIA_API_KEY = getattr(settings, 'DJELIA_API_KEY', 'YOUR_API_KEY')
DJELIA_BASE_URL = getattr(settings, 'DJELIA_BASE_URL', 'https://api.djelia.cloud/v2/')

# Configuration RobotMali et MALIBA-AI
ROBOTMALI_ASR_URL = getattr(settings, 'ROBOTMALI_ASR_URL', 'http://34.46.115.9:8080')
MALIBA_TTS_URL = getattr(settings, 'MALIBA_TTS_URL', 'http://34.46.115.9:8081')

# Dictionnaire de traduction simple pour le fallback
BAMARA_FRENCH_DICT = {
    "ɲɛnɛn": "maladie",
    "ɲɛnɛn": "souffrir",
    "ɲɛnɛn": "douleur",
    "ɲɛnɛn": "fièvre",
    "ɲɛnɛn": "toux",
    "ɲɛnɛn": "diarrhée",
    "ɲɛnɛn": "vomissement",
    "ɲɛnɛn": "fatigue",
    "ɲɛnɛn": "mal de tête",
    "ɲɛnɛn": "mal de ventre",
    "ɲɛnɛn": "paludisme",
    "ɲɛnɛn": "anémie",
    "ɲɛnɛn": "hypertension",
    "ɲɛnɛn": "diabète",
    "ɲɛnɛn": "grossesse",
    "ɲɛnɛn": "enfant",
    "ɲɛnɛn": "adulte",
    "ɲɛnɛn": "vieux",
    "ɲɛnɛn": "femme",
    "ɲɛnɛn": "homme",
}

# Conseils médicaux de base
MEDICAL_ADVICE = {
    "fièvre": "En cas de fièvre, prenez du paracétamol et consultez un médecin si la fièvre persiste plus de 3 jours.",
    "douleur": "Pour la douleur, prenez des antalgiques et consultez un centre de santé si la douleur est intense.",
    "toux": "Pour la toux, buvez beaucoup d'eau et consultez un médecin si la toux persiste.",
    "diarrhée": "En cas de diarrhée, buvez beaucoup d'eau et prenez des sels de réhydratation.",
    "vomissement": "En cas de vomissement, évitez de manger et consultez un médecin si cela persiste.",
    "fatigue": "Reposez-vous bien et mangez équilibré. Consultez un médecin si la fatigue persiste.",
    "mal de tête": "Reposez-vous dans un endroit calme et prenez du paracétamol si nécessaire.",
    "mal de ventre": "Évitez les aliments gras et consultez un médecin si la douleur persiste.",
    "paludisme": "Consultez immédiatement un centre de santé pour un test de paludisme.",
    "anémie": "Mangez des aliments riches en fer et consultez un médecin.",
    "hypertension": "Réduisez votre consommation de sel et consultez régulièrement un médecin.",
    "diabète": "Surveillez votre glycémie et suivez les conseils de votre médecin.",
    "grossesse": "Consultez régulièrement votre sage-femme ou médecin.",
}

def fallback_translate(text, direction):
    """Traduction de fallback simple"""
    if direction == "bam-fra":
        # Traduction bambara vers français (simplifiée)
        for bam, fra in BAMARA_FRENCH_DICT.items():
            if bam in text.lower():
                return f"Vous avez mentionné '{fra}'. "
        return f"Vous avez dit: {text}. "
    elif direction == "fra-bam":
        # Traduction français vers bambara (simplifiée)
        return f"Conseil médical: {text}"
    return text

def fallback_transcribe(audio_file):
    """Transcription de fallback - retourne un message d'aide"""
    return "Audio reçu. Veuillez décrire vos symptômes en texte pour recevoir des conseils médicaux."

def fallback_synthese(text):
    """Synthèse vocale de fallback - retourne None"""
    return None

def convert_audio_to_mono_16k(input_file, output_file=None):
    """
    Convertit un fichier audio en mono 16kHz WAV
    input_file: chemin du fichier d'entrée ou objet fichier
    output_file: chemin du fichier de sortie (optionnel)
    """
    try:
        # Créer un fichier temporaire si output_file n'est pas spécifié
        if output_file is None:
            temp_dir = tempfile.gettempdir()
            output_file = os.path.join(temp_dir, f"converted_{os.path.basename(str(input_file))}.wav")
        
        # Si c'est un objet fichier, le sauvegarder temporairement
        if hasattr(input_file, 'read'):
            temp_input = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_input.write(input_file.read())
            temp_input.close()
            input_path = temp_input.name
        else:
            input_path = str(input_file)
        
        # Conversion avec ffmpeg
        cmd = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", input_path,
            "-ac", "1",       # 1 canal (mono)
            "-ar", "16000",   # 16 kHz
            "-f", "wav",      # Format WAV
            output_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Nettoyer le fichier temporaire si créé
        if hasattr(input_file, 'read') and os.path.exists(input_path):
            os.unlink(input_path)
        
        if result.returncode == 0:
            logger.info(f"Conversion audio réussie: {output_file}")
            return output_file
        else:
            logger.error(f"Erreur conversion audio: {result.stderr}")
            return None
            
    except Exception as e:
        logger.error(f"Erreur lors de la conversion audio: {str(e)}")
        return None

def load_robotmali_model():
    """
    Charge le modèle RobotMali QuartzNet
    Retourne le modèle ou None si erreur
    """
    try:
        import nemo.collections.asr as nemo_asr
        model = nemo_asr.models.EncDecCTCModel.from_pretrained(
            model_name="RobotsMali/stt-bm-quartznet15x5-V0"
        )
        logger.info("Modèle RobotMali QuartzNet chargé avec succès")
        return model
    except Exception as e:
        logger.error(f"Erreur lors du chargement du modèle RobotMali: {str(e)}")
        return None

# Variable globale pour le modèle
_robotmali_model = None

def get_robotmali_model():
    """Retourne le modèle RobotMali (singleton)"""
    global _robotmali_model
    if _robotmali_model is None:
        _robotmali_model = load_robotmali_model()
    return _robotmali_model

# ASR avec QuartzNet de RobotMali
def transcrire(audio_file, translate_to_french=False):
    """
    Transcrit un fichier audio en texte utilisant QuartzNet de RobotMali
    audio_file: objet fichier ou chemin de fichier
    translate_to_french: si True, traduit directement en français
    """
    try:
        # Étape 1: Conversion audio en mono 16kHz
        converted_file = convert_audio_to_mono_16k(audio_file)
        if not converted_file:
            logger.error("Impossible de convertir l'audio")
            return fallback_transcribe(audio_file)
        
        # Étape 2: Charger le modèle RobotMali
        model = get_robotmali_model()
        if model is None:
            logger.error("Modèle RobotMali non disponible")
            return fallback_transcribe(audio_file)
        
        # Étape 3: Transcription avec le modèle
        try:
            # Transcription par batch (le modèle attend une liste)
            audio_paths = [converted_file]
            texts = model.transcribe(audio_paths, batch_size=1)
            
            if texts and len(texts) > 0:
                transcribed_text = texts[0].strip()
                logger.info(f"Transcription RobotMali: {transcribed_text}")
                
                # Nettoyer le fichier converti
                if os.path.exists(converted_file):
                    os.unlink(converted_file)
                
                return transcribed_text
            else:
                logger.error("Aucun texte transcrit")
                return fallback_transcribe(audio_file)
                
        except Exception as e:
            logger.error(f"Erreur lors de la transcription: {str(e)}")
            return fallback_transcribe(audio_file)
        
    except Exception as e:
        logger.error(f"Erreur lors de la transcription RobotMali: {str(e)}")
        return fallback_transcribe(audio_file)

# TTS avec MALIBA-AI
def synthese(text, lang='bam_Latn'):
    """
    Convertit un texte en audio utilisant MALIBA-AI TTS
    text: texte à synthétiser
    lang: langue du texte ('bam_Latn' pour bambara, 'fra_Latn' pour français)
    """
    try:
        # Configuration MALIBA-AI TTS
        endpoint = f"{MALIBA_TTS_URL}/predict"
        payload = {
            "text": text,
            "speaker_id": "Seydou",  # Voix bambara
            "temperature": 0.8,
            "top_k": 50,
            "top_p": 1.0,
            "max_new_audio_tokens": 2048
        }
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(endpoint, json=payload, headers=headers, timeout=180)
        
        if response.status_code == 200:
            logger.info(f"TTS MALIBA-AI réussi pour: {text[:50]}...")
            return response.content  # bytes (audio WAV)
        else:
            try:
                error_detail = response.json().get('detail', 'Unknown error')
                logger.error(f"Erreur TTS MALIBA-AI: {response.status_code} - {error_detail}")
            except:
                logger.error(f"Erreur TTS MALIBA-AI: {response.status_code} - {response.text}")
            return fallback_synthese(text)
            
    except requests.exceptions.Timeout:
        logger.error("Timeout TTS MALIBA-AI après 180 secondes")
        return fallback_synthese(text)
    except requests.exceptions.ConnectionError:
        logger.error(f"Impossible de se connecter au serveur TTS MALIBA-AI: {MALIBA_TTS_URL}")
        return fallback_synthese(text)
    except Exception as e:
        logger.error(f"Erreur lors de la synthèse vocale MALIBA-AI: {str(e)}")
        return fallback_synthese(text)

# Traduction (format JSON clé/valeur)
def traduire(text, direction):
    """
    Traduit un texte entre bambara et français
    direction: 'bam-fra' ou 'fra-bam'
    """
    try:
        url = DJELIA_BASE_URL + 'translate/'
        headers = {"x-api-key": DJELIA_API_KEY, "Content-Type": "application/json"}
        
        # Déterminer source et target à partir de direction
        if direction == "bam-fra":
            source, target = "bam_Latn", "fra_Latn"
        elif direction == "fra-bam":
            source, target = "fra_Latn", "bam_Latn"
        else:
            logger.error(f"Direction de traduction invalide: {direction}")
            return fallback_translate(text, direction)
        
        data = {
            "text": text,
            "source": source,
            "target": target
        }
        
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=30)
        
        if response.ok:
            result = response.json()
            return result.get('translation', text)
        else:
            logger.error(f"Erreur API traduction: {response.status_code} - {response.text}")
            return fallback_translate(text, direction)
            
    except Exception as e:
        logger.error(f"Erreur lors de la traduction: {str(e)}")
        return fallback_translate(text, direction)

# Recherche médicale via DuckDuckGo
def duckduck_medical_search(query):
    """
    Recherche des informations médicales fiables
    query: requête de recherche
    """
    try:
        # Recherche sur des sites médicaux fiables
        medical_sites = "site:who.int OR site:unicef.org OR site:msf.org OR site:vidal.fr"
        search_query = f"{query} {medical_sites}"
        url = f'https://duckduckgo.com/html/?q={quote_plus(search_query)}'
        
        response = requests.get(url, timeout=30)
        
        if response.ok:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.find_all('a', class_='result__a')
            
            if results:
                return results[0].get_text().strip()
        
        return "Aucun résultat médical fiable trouvé pour cette recherche."
        
    except Exception as e:
        logger.error(f"Erreur lors de la recherche médicale: {str(e)}")
        return "Erreur lors de la recherche d'informations médicales."

def recherche_pipeline(sympt_input, user=None, is_audio=False):
    """
    Pipeline complet de traitement médical:
    1. Transcription si audio (RobotMali QuartzNet)
    2. Traduction en français
    3. Recherche médicale
    4. Traduction des résultats
    5. Synthèse vocale (MALIBA-AI TTS)
    """
    try:
        # Étape 1: Transcription si audio
        if is_audio:
            sympt_bam = transcrire(sympt_input)
            logger.info(f"Transcription audio (RobotMali): {sympt_bam}")
        else:
            sympt_bam = sympt_input
        
        if not sympt_bam or sympt_bam.startswith("Erreur"):
            return {
                "success": False,
                "error": "Impossible de traiter l'audio ou le texte fourni",
                "symptomes_bam": sympt_bam,
                "symptomes_fr": "",
                "reponse_bam": "Veuillez réessayer avec un enregistrement plus clair."
            }
        
        # Étape 2: Traduction en français
        sympt_fr = traduire(sympt_bam, "bam-fra")
        logger.info(f"Traduction en français: {sympt_fr}")
        
        # Étape 3: Recherche médicale
        conseils_fr = duckduck_medical_search(sympt_fr)
        logger.info(f"Recherche médicale: {conseils_fr[:100]}...")
        
        # Étape 4: Traduction des résultats
        reponse_bam = traduire(conseils_fr, "fra-bam")
        logger.info(f"Traduction réponse: {reponse_bam[:100]}...")
        
        # Étape 5: Synthèse vocale (MALIBA-AI)
        audio_bytes = synthese(reponse_bam)
        
        # Sauvegarde en base si utilisateur authentifié
        recherche = None
        if user and user.is_authenticated:
            from .models import Recherche
            from django.core.files.base import ContentFile
            
            recherche = Recherche.objects.create(
                user=user,
                audio=sympt_input if is_audio else None,
                symptomes_bam=sympt_bam,
                symptomes_fr=sympt_fr,
                reponse_bam=reponse_bam
            )
            
            if audio_bytes:
                fname = f"reponses/{reponse_bam[:50]}_{user.id}.wav".replace(" ", "_")
                recherche.reponse_mp3.save(fname, ContentFile(audio_bytes))
                recherche.save()
        
        return {
            "success": True,
            "symptomes_bam": sympt_bam,
            "symptomes_fr": sympt_fr,
            "reponse_bam": reponse_bam,
            "audio_url": recherche.reponse_mp3.url if recherche and audio_bytes else None,
            "recherche_id": recherche.id if recherche else None
        }
    
    except Exception as e:
        logger.error(f"Erreur dans le pipeline de recherche: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "symptomes_bam": "",
            "symptomes_fr": "",
            "reponse_bam": "Une erreur est survenue lors du traitement. Veuillez réessayer."
        }