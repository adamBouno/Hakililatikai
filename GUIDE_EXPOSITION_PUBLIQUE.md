# 🌐 Guide d'exposition publique du serveur Colab

## 🎯 Objectif
Exposer le serveur Colab RobotMali avec une URL publique pour que Django puisse y accéder.

## 📋 Instructions dans Google Colab

### 1. Ouvrir le fichier
Ouvrez `colab_robotmali_working.py` dans Google Colab.

### 2. Exécuter le serveur
Dans Colab, exécutez :
```python
start_flask_with_gradio()
```

### 3. Récupérer l'URL publique
Vous obtiendrez une sortie comme :
```
✅ API Flask exposée publiquement: https://xxxx.gradio.live
📝 Endpoints disponibles:
   - Transcription: https://xxxx.gradio.live
   - Santé: https://xxxx.gradio.live
```

## 🔧 Configuration Django

### 1. Mettre à jour la configuration
Dans votre fichier `.env` ou `env.example`, remplacez :
```
COLAB_NOTEBOOK_URL=https://xxxx.gradio.live
```

### 2. Redémarrer Django
```bash
python manage.py runserver
```

## 🧪 Test de connexion

### Test avec curl :
```bash
curl https://xxxx.gradio.live
```

### Test avec le script Python :
```python
import requests

# Test de santé
response = requests.get('https://xxxx.gradio.live')
print(response.status_code)
```

## 🎤 Test de transcription

### Via l'interface Gradio :
1. Allez sur l'URL fournie par Gradio
2. Enregistrez un audio
3. Cliquez sur "🎤 Transcrire"
4. Vérifiez la transcription

### Via Django :
1. Allez sur votre page symptômes
2. Enregistrez un audio
3. Vérifiez que la transcription s'affiche

## ⚠️ Notes importantes

1. **L'URL Gradio change à chaque redémarrage**
2. **Gardez Colab ouvert** pour maintenir le serveur actif
3. **L'URL est publique** - ne partagez pas de données sensibles
4. **Timeout possible** - les requêtes peuvent prendre du temps

## 🔄 En cas de problème

### Si l'URL ne fonctionne pas :
1. Vérifiez que Colab est toujours actif
2. Redémarrez le serveur dans Colab
3. Récupérez la nouvelle URL
4. Mettez à jour Django

### Si la transcription échoue :
1. Vérifiez les logs dans Colab
2. Testez avec un audio court
3. Vérifiez que le modèle est chargé

## ✅ Avantages de cette approche

- ✅ **Pas besoin de compte ngrok**
- ✅ **Exposition automatique** avec Gradio
- ✅ **Interface de test intégrée**
- ✅ **URL publique stable** pendant la session
- ✅ **Facile à configurer**

## 🚀 Prochaines étapes

1. **Tester la connexion** avec l'URL Gradio
2. **Mettre à jour Django** avec la nouvelle URL
3. **Tester la page symptômes** avec transcription
4. **Optimiser les performances** si nécessaire 