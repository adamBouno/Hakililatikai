import requests
import json
import base64
import os
from django.conf import settings
import tempfile
import subprocess
from .utils_simple import recherche_medicale_simple, traduire_bambara_francais

class ColabASRProcessor:
    """
    Processeur ASR utilisant Google Colab comme espace de traitement
    """
    
    def __init__(self):
        self.colab_url = getattr(settings, 'COLAB_NOTEBOOK_URL', None)
        self.api_key = getattr(settings, 'COLAB_API_KEY', None)
        
    def convertir_audio(self, audio_file_path):
        """
        Convertit l'audio en format compatible (mono 16kHz WAV)
        """
        try:
            # Créer un fichier temporaire pour la conversion
            temp_output = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_output.close()
            
            # Commande FFmpeg pour conversion
            cmd = [
                'ffmpeg', '-i', audio_file_path,
                '-ac', '1',  # mono
                '-ar', '16000',  # 16kHz
                '-f', 'wav',
                temp_output.name,
                '-y'  # écraser si existe
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return temp_output.name
            else:
                print(f"Erreur conversion audio: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"Erreur lors de la conversion audio: {e}")
            return None
    
    def envoyer_audio_colab(self, audio_file_path):
        """
        Envoie l'audio à Google Colab pour transcription
        """
        try:
            # Convertir l'audio
            audio_converted = self.convertir_audio(audio_file_path)
            if not audio_converted:
                return None
            
            # Lire le fichier audio en base64
            with open(audio_converted, 'rb') as f:
                audio_base64 = base64.b64encode(f.read()).decode('utf-8')
            
            # Nettoyer le fichier temporaire
            os.unlink(audio_converted)
            
            # Préparer les données pour Colab
            payload = {
                'audio_data': audio_base64,
                'model_name': 'RobotsMali/stt-bm-quartznet15x5-V0'
            }
            
            # Envoyer à Colab via l'URL Gradio
            if self.colab_url:
                try:
                    # Test de santé d'abord
                    health_response = requests.get(self.colab_url, timeout=10)
                    if health_response.status_code == 200:
                        print(f"✅ Serveur Colab accessible: {self.colab_url}")
                        
                        # Pour l'instant, utiliser l'interface Gradio
                        # L'URL Gradio expose une interface web, pas des endpoints API
                        # On va utiliser une approche différente
                        return self.transcription_via_gradio(audio_base64)
                    else:
                        print(f"❌ Serveur Colab non accessible: {health_response.status_code}")
                        return self.transcription_fallback(audio_file_path)
                        
                except Exception as e:
                    print(f"❌ Erreur connexion Colab: {e}")
                    return self.transcription_fallback(audio_file_path)
            
            # Fallback vers traitement local simple
            return self.transcription_fallback(audio_file_path)
            
        except Exception as e:
            print(f"Erreur lors de l'envoi à Colab: {e}")
            return self.transcription_fallback(audio_file_path)
    
    def transcription_fallback(self, audio_file_path):
        """
        Fallback vers transcription simple ou interface manuelle
        """
        # Pour l'instant, retourner un message demandant la saisie manuelle
        return "Veuillez saisir vos symptômes en texte"
    
    def transcription_via_gradio(self, audio_base64):
        """
        Transcription via l'interface Gradio (approche temporaire)
        """
        try:
            # Pour l'instant, retourner un message indiquant que l'interface est disponible
            gradio_url = self.colab_url
            return f"Audio reçu. Interface de transcription disponible sur: {gradio_url}"
            
        except Exception as e:
            print(f"Erreur transcription Gradio: {e}")
            return "Erreur de transcription"
    
    def synthese_vocale_colab(self, texte, langue='bambara'):
        """
        Utilise Colab pour la synthèse vocale
        """
        try:
            payload = {
                'text': texte,
                'language': langue,
                'voice': 'seydou',  # voix RobotMali
                'task': 'tts'
            }
            
            if self.colab_url:
                response = requests.post(
                    self.colab_url,
                    json=payload,
                    headers={'Authorization': f'Bearer {self.api_key}'} if self.api_key else {}
                )
                
                if response.status_code == 200:
                    audio_data = response.json().get('audio_data')
                    if audio_data:
                        # Décoder et sauvegarder l'audio
                        audio_bytes = base64.b64decode(audio_data)
                        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                        temp_file.write(audio_bytes)
                        temp_file.close()
                        return temp_file.name
            
            # Fallback vers TTS simple
            return self.tts_fallback(texte)
            
        except Exception as e:
            print(f"Erreur synthèse vocale Colab: {e}")
            return self.tts_fallback(texte)
    
    def tts_fallback(self, texte):
        """
        Fallback pour TTS (peut être étendu avec pyttsx3 ou autre)
        """
        # Pour l'instant, retourner None (pas de TTS)
        return None

def recherche_pipeline_colab(audio_file_path):
    """
    Pipeline complet utilisant Google Colab
    """
    processor = ColabASRProcessor()
    
    # 1. Transcription via Colab
    transcription = processor.envoyer_audio_colab(audio_file_path)
    
    if not transcription or transcription == "Veuillez saisir vos symptômes en texte":
        return {
            'transcription': transcription,
            'traduction': '',
            'conseils': 'Veuillez saisir vos symptômes manuellement',
            'audio_reponse': None,
            'mode': 'manuel'
        }
    
    # 2. Traduction bambara -> français
    traduction = traduire_bambara_francais(transcription)
    
    # 3. Recherche médicale
    conseils = recherche_medicale_simple(traduction)
    
    # 4. Synthèse vocale via Colab
    audio_reponse = processor.synthese_vocale_colab(conseils)
    
    return {
        'transcription': transcription,
        'traduction': traduction,
        'conseils': conseils,
        'audio_reponse': audio_reponse,
        'mode': 'colab'
    } 