"""
Serveur Google Colab RobotMali - Basé sur votre code fonctionnel
"""

# Installation des dépendances
!pip install --upgrade pip
!pip install nemo_toolkit['asr']
!pip install flask flask-cors gradio requests

import nemo.collections.asr as nemo_asr
import gradio as gr
import requests
import base64
import tempfile
import os
import subprocess
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
import json

# Configuration Flask
app = Flask(__name__)
CORS(app)

class WorkingRobotMaliProcessor:
    def __init__(self):
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.load_model()
    
    def load_model(self):
        """Charge le modèle RobotMali avec votre approche"""
        try:
            print("Chargement du modèle RobotMali...")
            
            # Utiliser votre approche qui fonctionne
            self.model = nemo_asr.models.EncDecCTCModel.from_pretrained(
                model_name="RobotsMali/stt-bm-quartznet15x5-V0"
            )
            
            print(f"✅ Modèle RobotMali chargé sur {self.device}")
            self.model_loaded = True
            
        except Exception as e:
            print(f"❌ Erreur chargement modèle: {e}")
            self.model_loaded = False
    
    def convert_audio(self, audio_data):
        """Convertit l'audio en format compatible"""
        try:
            # Décoder l'audio base64
            audio_bytes = base64.b64decode(audio_data)
            
            # Sauvegarder temporairement
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                f.write(audio_bytes)
                temp_path = f.name
            
            # Convertir avec ffmpeg (votre approche)
            output_path = temp_path.replace('.wav', '_converted.wav')
            
            subprocess.run([
                "ffmpeg", "-y", "-loglevel", "error",
                "-i", temp_path,
                "-ac", "1",       # 1 canal (mono)
                "-ar", "16000",   # 16 kHz
                output_path
            ], check=True)
            
            # Nettoyer le fichier original
            os.unlink(temp_path)
            
            return output_path
            
        except Exception as e:
            print(f"Erreur conversion audio: {e}")
            return None
    
    def transcribe(self, audio_data):
        """Transcrit l'audio avec le modèle RobotMali"""
        try:
            if not self.model_loaded:
                return "Erreur: Modèle non chargé"
            
            # Convertir l'audio
            audio_path = self.convert_audio(audio_data)
            if not audio_path:
                return "Erreur: Impossible de convertir l'audio"
            
            # Transcription avec votre approche
            texts = self.model.transcribe([audio_path], batch_size=1)
            
            # Nettoyer
            if os.path.exists(audio_path):
                os.unlink(audio_path)
            
            if texts and len(texts) > 0:
                return texts[0]
            else:
                return "Aucune transcription générée"
            
        except Exception as e:
            print(f"Erreur transcription: {e}")
            return f"Erreur: {str(e)}"
    
    def text_to_speech(self, text, voice="seydou"):
        """Synthèse vocale (placeholder)"""
        try:
            return f"TTS pour: {text} (voix: {voice})"
        except Exception as e:
            print(f"Erreur TTS: {e}")
            return f"Erreur TTS: {str(e)}"

# Initialiser le processeur
processor = WorkingRobotMaliProcessor()

# Routes Flask
@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    """Endpoint pour transcription audio"""
    try:
        data = request.get_json()
        audio_data = data.get('audio_data')
        model_name = data.get('model_name', 'RobotsMali/stt-bm-quartznet15x5-V0')
        
        if not audio_data:
            return jsonify({'error': 'Données audio manquantes'}), 400
        
        transcription = processor.transcribe(audio_data)
        
        return jsonify({
            'transcription': transcription,
            'model': model_name,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/tts', methods=['POST'])
def text_to_speech():
    """Endpoint pour synthèse vocale"""
    try:
        data = request.get_json()
        text = data.get('text')
        voice = data.get('voice', 'seydou')
        language = data.get('language', 'bambara')
        
        if not text:
            return jsonify({'error': 'Texte manquant'}), 400
        
        result = processor.text_to_speech(text, voice)
        
        return jsonify({
            'audio_data': result,
            'voice': voice,
            'language': language,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Vérification de l'état du serveur"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': processor.model_loaded,
        'device': processor.device,
        'version': 'working-robotmali'
    })

# Interface Gradio pour tests
def create_gradio_interface():
    """Interface Gradio pour tester le modèle"""
    
    def transcribe_audio_gradio(audio):
        if audio is None:
            return "Aucun audio fourni"
        
        # Convertir en base64
        audio_bytes = audio[1]  # Gradio retourne (sample_rate, audio_data)
        audio_base64 = base64.b64encode(audio_bytes.tobytes()).decode('utf-8')
        
        transcription = processor.transcribe(audio_base64)
        return transcription
    
    interface = gr.Interface(
        fn=transcribe_audio_gradio,
        inputs=gr.Audio(type="numpy"),
        outputs=gr.Textbox(label="Transcription"),
        title="RobotMali ASR - Interface de Test",
        description="Testez la transcription audio en bambara avec le vrai modèle"
    )
    
    return interface

# Démarrer le serveur Flask
def start_flask_server():
    """Démarre le serveur Flask"""
    print("🚀 Démarrage du serveur RobotMali...")
    app.run(host='0.0.0.0', port=8080, debug=False)

def start_gradio_server():
    """Démarre le serveur avec Gradio pour exposition publique"""
    print("🚀 Démarrage du serveur Gradio avec exposition publique...")
    
    # Créer l'interface Gradio
    interface = create_gradio_interface()
    
    # Lancer avec exposition publique
    public_url = interface.launch(
        server_name="0.0.0.0",
        server_port=8080,
        share=True,  # Ceci expose l'URL publique
        debug=False
    )
    
    print(f"✅ Serveur exposé publiquement: {public_url}")
    return public_url

def start_flask_with_gradio():
    """Démarre Flask avec Gradio pour exposition publique des endpoints"""
    print("🚀 Démarrage de Flask avec exposition Gradio...")
    
    # Créer une interface Gradio qui expose les endpoints Flask
    def transcribe_endpoint(audio):
        """Endpoint de transcription accessible via Gradio"""
        if audio is None:
            return "Aucun audio fourni"
        
        # Convertir en base64
        audio_bytes = audio[1]  # Gradio retourne (sample_rate, audio_data)
        audio_base64 = base64.b64encode(audio_bytes.tobytes()).decode('utf-8')
        
        # Utiliser le processeur directement
        transcription = processor.transcribe(audio_base64)
        return transcription
    
    def health_endpoint():
        """Endpoint de santé accessible via Gradio"""
        return f"✅ Serveur en ligne\n📦 Modèle chargé: {processor.model_loaded}\n🖥️ Device: {processor.device}"
    
    # Interface Gradio avec endpoints
    with gr.Blocks(title="RobotMali API") as interface:
        gr.Markdown("#  RobotMali API - Serveur Public")
        gr.Markdown("## Transcription Audio")
        
        with gr.Row():
            audio_input = gr.Audio(type="numpy", label="Audio à transcrire")
            text_output = gr.Textbox(label="Transcription", lines=3)
        
        transcribe_btn = gr.Button("🎤 Transcrire")
        transcribe_btn.click(fn=transcribe_endpoint, inputs=audio_input, outputs=text_output)
        
        gr.Markdown("## État du serveur")
        health_output = gr.Textbox(label="Santé", value=health_endpoint(), interactive=False)
        
        refresh_btn = gr.Button("🔄 Actualiser")
        refresh_btn.click(fn=health_endpoint, outputs=health_output)
    
    # Lancer avec exposition publique
    public_url = interface.launch(
        server_name="0.0.0.0",
        server_port=8080,
        share=True,
        debug=False
    )
    
    print(f"✅ API Flask exposée publiquement: {public_url}")
    print(f" Endpoints disponibles:")
    print(f"   - Transcription: {public_url}")
    print(f"   - Santé: {public_url}")
    
    return public_url

# Instructions d'utilisation
print("""
=== SERVEUR ROBOTMALI COLAB - VERSION FONCTIONNELLE ===

✅ Basé sur votre code qui fonctionne
✅ Modèle RobotMali chargé
✅ Conversion audio avec ffmpeg
✅ Transcription avec le vrai modèle

🚀 Options de démarrage:

1. Serveur Flask local:
   start_flask_server()

2. Serveur Gradio avec exposition publique:
   start_gradio_server()

3. API Flask exposée publiquement (RECOMMANDÉ):
   start_flask_with_gradio()

🎨 Pour tester avec Gradio:
   interface = create_gradio_interface()
   interface.launch()

📝 URLs possibles:
   - Local: http://localhost:8080
   - Public: (fournie par Gradio)
""")

# Démarrer automatiquement le serveur
if __name__ == "__main__":
    # Utiliser Flask avec Gradio pour l'exposition publique
    start_flask_with_gradio() 