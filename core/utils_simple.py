"""
Version simplifiée de transcription audio sans NeMo
Utilise des APIs externes ou des modèles plus légers
"""

import requests
import json
import tempfile
import os
import subprocess
from typing import Union
import logging

logger = logging.getLogger(__name__)

def convert_audio_to_mono_16k(input_file, output_file=None):
    """
    Convertit un fichier audio en mono 16kHz WAV
    """
    try:
        if output_file is None:
            temp_dir = tempfile.gettempdir()
            output_file = os.path.join(temp_dir, f"converted_{os.path.basename(str(input_file))}.wav")
        
        if hasattr(input_file, 'read'):
            temp_input = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_input.write(input_file.read())
            temp_input.close()
            input_path = temp_input.name
        else:
            input_path = str(input_file)
        
        cmd = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", input_path,
            "-ac", "1",
            "-ar", "16000",
            "-f", "wav",
            output_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
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

def transcrire_simple(audio_file):
    """
    Transcription simple utilisant des APIs externes
    """
    try:
        # Option 1: Utiliser une API de transcription gratuite
        # (Vous pouvez remplacer par votre API préférée)
        
        # Pour l'instant, retourner un message d'aide
        return "Audio reçu. Veuillez décrire vos symptômes en texte pour recevoir des conseils médicaux."
        
    except Exception as e:
        logger.error(f"Erreur transcription simple: {str(e)}")
        return "Erreur lors de la transcription audio."

def synthese_simple(text):
    """
    Synthèse vocale simple
    """
    try:
        # Utiliser MALIBA-AI TTS si disponible
        from .utils import synthese
        return synthese(text)
    except:
        # Fallback: pas de synthèse vocale
        return None

def recherche_medicale_simple(symptomes_fr):
    """
    Recherche médicale simple basée sur les symptômes
    """
    try:
        # Recherche simple avec DuckDuckGo
        from .utils import duckduck_medical_search
        return duckduck_medical_search(symptomes_fr)
    except Exception as e:
        logger.error(f"Erreur recherche médicale: {str(e)}")
        return "Consultez un médecin pour un diagnostic précis."

def traduire_bambara_francais(texte_bambara):
    """
    Traduction bambara vers français
    """
    try:
        # Utiliser la fonction de traduction existante
        from .utils import fallback_translate
        return fallback_translate(texte_bambara, "bam-fra")
    except Exception as e:
        logger.error(f"Erreur traduction: {str(e)}")
        return "Traduction non disponible"

def recherche_pipeline_simple(sympt_input, user=None, is_audio=False):
    """
    Pipeline simplifié sans NeMo
    """
    try:
        if is_audio:
            sympt_bam = transcrire_simple(sympt_input)
        else:
            sympt_bam = sympt_input
        
        if not sympt_bam:
            return {
                "success": False,
                "error": "Impossible de traiter l'audio ou le texte",
                "reponse_bam": "Veuillez décrire vos symptômes en texte."
            }
        
        # Utiliser le système de fallback pour la traduction
        from .utils import fallback_translate, duckduck_medical_search
        
        sympt_fr = fallback_translate(sympt_bam, "bam-fra")
        conseils_fr = duckduck_medical_search(sympt_fr)
        reponse_bam = fallback_translate(conseils_fr, "fra-bam")
        
        # Sauvegarde
        if user and user.is_authenticated:
            from .models import Recherche
            recherche = Recherche.objects.create(
                user=user,
                audio=sympt_input if is_audio else None,
                symptomes_bam=sympt_bam,
                symptomes_fr=sympt_fr,
                reponse_bam=reponse_bam
            )
        
        return {
            "success": True,
            "symptomes_bam": sympt_bam,
            "symptomes_fr": sympt_fr,
            "reponse_bam": reponse_bam,
            "recherche_id": recherche.id if 'recherche' in locals() else None
        }
    
    except Exception as e:
        logger.error(f"Erreur pipeline simple: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "reponse_bam": "Une erreur est survenue. Veuillez réessayer."
        } 