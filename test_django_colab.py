#!/usr/bin/env python3
"""
Test de la configuration Django avec l'URL Colab
"""

import os
import django
from django.conf import settings

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rassure_moi.settings')
django.setup()

def test_colab_config():
    """Test de la configuration Colab dans Django"""
    print("🔧 Test de la configuration Django avec Colab")
    print("=" * 50)
    
    # Vérifier l'URL Colab
    colab_url = getattr(settings, 'COLAB_NOTEBOOK_URL', '')
    print(f"🌐 URL Colab configurée: {colab_url}")
    
    if colab_url:
        print("✅ URL Colab trouvée dans les paramètres")
        
        # Test de connexion
        try:
            import requests
            response = requests.get(colab_url, timeout=10)
            print(f"✅ Serveur Colab accessible: HTTP {response.status_code}")
            
            if response.status_code == 200:
                print("🎉 Configuration réussie !")
                print("🚀 Vous pouvez maintenant tester sur l'application Django")
                print("📱 Allez sur: http://127.0.0.1:8000/symptomes/")
            else:
                print(f"⚠️ Serveur répond mais avec le code: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            print("💡 Vérifiez que le serveur Colab est actif")
    else:
        print("❌ URL Colab non configurée")
        print("💡 Vérifiez le fichier .env")

if __name__ == "__main__":
    test_colab_config() 