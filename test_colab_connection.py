#!/usr/bin/env python3
"""
Script de test pour vérifier la connexion au serveur Colab RobotMali
"""

import requests
import json
import base64
import numpy as np
import time

def test_colab_health():
    """Test de santé du serveur Colab"""
    try:
        print("🏥 Test de santé du serveur Colab...")
        response = requests.get('https://e1aa29361922a079c2.gradio.live', timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Serveur en ligne: HTTP {response.status_code}")
            return True
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur Colab")
        print("💡 Vérifiez que le serveur est démarré sur https://e1aa29361922a079c2.gradio.live")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_transcription():
    """Test de transcription avec audio minimal"""
    try:
        print("🎤 Test de transcription...")
        
        # Créer un audio de test (1 seconde de silence)
        test_audio = np.zeros(16000, dtype=np.int16)
        audio_base64 = base64.b64encode(test_audio.tobytes()).decode('utf-8')
        
        payload = {
            'audio_data': audio_base64,
            'model_name': 'RobotsMali/stt-bm-quartznet15x5-V0'
        }
        
        start_time = time.time()
        response = requests.post(
            'https://e1aa29361922a079c2.gradio.live/transcribe',
            json=payload,
            timeout=30
        )
        processing_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Transcription réussie en {processing_time:.2f}s")
            print(f"📝 Résultat: {data.get('transcription', '')}")
            return True
        else:
            print(f"❌ Erreur transcription: {response.status_code}")
            print(f"📄 Détails: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Timeout lors de la transcription")
        return False
    except Exception as e:
        print(f"❌ Erreur transcription: {e}")
        return False

def main():
    """Test principal"""
    print("🚀 Test de connexion au serveur Colab RobotMali")
    print("=" * 50)
    print(f"🌐 URL testée: https://e1aa29361922a079c2.gradio.live")
    print("=" * 50)
    
    # Test de santé
    health_ok = test_colab_health()
    
    if health_ok:
        print("\n" + "=" * 50)
        # Test de transcription
        transcription_ok = test_transcription()
        
        if transcription_ok:
            print("\n🎉 Tous les tests sont passés !")
            print("✅ Le serveur Colab fonctionne correctement")
            print("🚀 Vous pouvez maintenant tester sur votre application Django !")
        else:
            print("\n⚠️ Le serveur répond mais la transcription échoue")
            print("💡 Vérifiez les logs Colab pour plus de détails")
    else:
        print("\n❌ Le serveur Colab n'est pas accessible")
        print("💡 Vérifiez que le serveur est démarré dans Colab")
        print("💡 URL attendue: https://e1aa29361922a079c2.gradio.live")

if __name__ == "__main__":
    main() 