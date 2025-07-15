# 🚀 Guide d'utilisation du serveur Colab RobotMali

##  Serveur fonctionnel

Le serveur Colab qui fonctionne est dans le fichier : `colab_robotmali_working.py`

### URL du serveur : `http://127.0.0.1:5000`

## 📋 Instructions d'utilisation

### 1. Dans Google Colab

1. **Ouvrir le fichier** `colab_robotmali_working.py` dans Colab
2. **Exécuter toutes les cellules** pour installer les dépendances
3. **Démarrer le serveur** :
   ```python
   start_flask_server()
   ```

### 2. Configuration Django

Le fichier `env.example` contient la configuration correcte :
```
COLAB_NOTEBOOK_URL=http://127.0.0.1:5000
```

### 3. Test du serveur

#### Test de santé :
```bash
curl http://127.0.0.1:5000/health
```

#### Test de transcription :
```bash
curl -X POST http://127.0.0.1:5000/transcribe \
  -H "Content-Type: application/json" \
  -d '{"audio_data": "base64_audio_data"}'
```

### 4. Interface de test

Dans Colab, vous pouvez aussi utiliser l'interface Gradio :
```python
interface = create_gradio_interface()
interface.launch()
```

## 🔧 Endpoints disponibles

- `GET /health` - État du serveur
- `POST /transcribe` - Transcription audio
- `POST /tts` - Synthèse vocale (placeholder)

## 📝 Exemple d'utilisation

### Transcription audio :
```python
import requests
import base64

# Lire un fichier audio
with open('audio.wav', 'rb') as f:
    audio_data = base64.b64encode(f.read()).decode('utf-8')

# Envoyer à Colab
response = requests.post('http://127.0.0.1:5000/transcribe', 
                        json={'audio_data': audio_data})

print(response.json())
```

##  Notes importantes

1. **Le serveur fonctionne sur le port 5000** dans Colab
2. **Utilisez l'URL `http://127.0.0.1:5000`** pour les requêtes
3. **Le modèle RobotMali est préchargé** et optimisé
4. **Conversion audio automatique** avec ffmpeg


