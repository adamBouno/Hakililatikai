from django.core.management.base import BaseCommand
from django.conf import settings
import requests
import json

class Command(BaseCommand):
    help = 'Vérifie la configuration audio et API Djelia'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Diagnostic de la configuration audio ==='))
        
        # Vérifier la clé API
        api_key = getattr(settings, 'DJELIA_API_KEY', '')
        if not api_key or api_key == 'YOUR_DJELIA_API_KEY':
            self.stdout.write(
                self.style.ERROR('❌ Clé API Djelia non configurée')
            )
            self.stdout.write(
                self.style.WARNING('→ Créez un fichier .env avec DJELIA_API_KEY=votre_clé_api')
            )
            return
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ Clé API Djelia configurée')
            )
        
        # Tester la connexion à l'API
        self.stdout.write('\n=== Test de connexion API ===')
        try:
            url = 'https://djelia.cloud/api/v2/models/translate/'
            headers = {"x-api-key": api_key, "Content-Type": "application/json"}
            data = {
                "text": "test",
                "source": "fra_Latn",
                "target": "bam_Latn"
            }
            
            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=10)
            
            if response.ok:
                self.stdout.write(
                    self.style.SUCCESS('✅ API Djelia accessible')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Erreur API: {response.status_code} - {response.text}')
                )
                
        except requests.exceptions.RequestException as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur de connexion: {str(e)}')
            )
        
        # Vérifier les dossiers media
        self.stdout.write('\n=== Vérification des dossiers ===')
        import os
        
        media_root = getattr(settings, 'MEDIA_ROOT', 'media')
        symptomes_dir = os.path.join(media_root, 'symptomes')
        reponses_dir = os.path.join(media_root, 'reponses')
        
        for directory in [media_root, symptomes_dir, reponses_dir]:
            if os.path.exists(directory):
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Dossier existant: {directory}')
                )
            else:
                try:
                    os.makedirs(directory, exist_ok=True)
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Dossier créé: {directory}')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Erreur création dossier {directory}: {str(e)}')
                    )
        
        self.stdout.write('\n=== Instructions de configuration ===')
        self.stdout.write('1. Obtenez une clé API Djelia sur https://djelia.cloud')
        self.stdout.write('2. Créez un fichier .env à la racine du projet')
        self.stdout.write('3. Ajoutez: DJELIA_API_KEY=votre_clé_api')
        self.stdout.write('4. Redémarrez le serveur Django')
        self.stdout.write('\n=== Test de transcription ===')
        self.stdout.write('Pour tester la transcription, utilisez la page web ou:')
        self.stdout.write('python manage.py shell')
        self.stdout.write('>>> from core.utils import transcrire')
        self.stdout.write('>>> transcrire("chemin/vers/fichier.audio")') 