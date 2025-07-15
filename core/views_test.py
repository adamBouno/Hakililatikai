from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
import base64
import tempfile
import os
from django.conf import settings
import requests

@login_required
def test_colab_interface(request):
    """
    Interface de test intégrée à Django pour tester la transcription Colab
    """
    return render(request, 'core/test_colab.html')

@csrf_exempt
def test_transcription_api(request):
    """
    API pour tester la transcription via Colab
    """
    if request.method == 'POST':
        try:
            # Récupérer l'audio depuis la requête
            audio_file = request.FILES.get('audio')
            
            if not audio_file:
                return JsonResponse({
                    'success': False,
                    'error': 'Aucun fichier audio fourni'
                })
            
            # Convertir l'audio en base64
            audio_bytes = audio_file.read()
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            # Envoyer à Colab
            colab_url = getattr(settings, 'COLAB_NOTEBOOK_URL', '')
            if not colab_url:
                return JsonResponse({
                    'success': False,
                    'error': 'URL Colab non configurée'
                })
            
            # Préparer la requête
            payload = {
                'audio_data': audio_base64,
                'model_name': 'RobotsMali/stt-bm-quartznet15x5-V0'
            }
            
            # Envoyer à Colab
            response = requests.post(
                f"{colab_url}/transcribe",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return JsonResponse({
                    'success': True,
                    'transcription': data.get('transcription', ''),
                    'model': data.get('model', ''),
                    'status': data.get('status', '')
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Erreur Colab: {response.status_code}',
                    'details': response.text
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erreur: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Méthode non autorisée'
    })

@csrf_exempt
def test_colab_health(request):
    """
    Test de santé du serveur Colab
    """
    try:
        colab_url = getattr(settings, 'COLAB_NOTEBOOK_URL', '')
        if not colab_url:
            return JsonResponse({
                'success': False,
                'error': 'URL Colab non configurée'
            })
        
        response = requests.get(f"{colab_url}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return JsonResponse({
                'success': True,
                'status': data.get('status', ''),
                'model_loaded': data.get('model_loaded', False),
                'device': data.get('device', ''),
                'version': data.get('version', '')
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'Erreur HTTP {response.status_code}',
                'details': response.text
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur de connexion: {str(e)}'
        })

@login_required
def test_batch_transcription(request):
    """
    Interface pour tester la transcription par batch
    """
    if request.method == 'POST':
        try:
            audio_files = request.FILES.getlist('audio_files')
            
            if not audio_files:
                return JsonResponse({
                    'success': False,
                    'error': 'Aucun fichier audio fourni'
                })
            
            colab_url = getattr(settings, 'COLAB_NOTEBOOK_URL', '')
            if not colab_url:
                return JsonResponse({
                    'success': False,
                    'error': 'URL Colab non configurée'
                })
            
            results = []
            for audio_file in audio_files:
                # Convertir en base64
                audio_bytes = audio_file.read()
                audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                
                # Envoyer à Colab
                payload = {
                    'audio_data': audio_base64,
                    'model_name': 'RobotsMali/stt-bm-quartznet15x5-V0'
                }
                
                response = requests.post(
                    f"{colab_url}/transcribe",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results.append({
                        'filename': audio_file.name,
                        'transcription': data.get('transcription', ''),
                        'status': 'success'
                    })
                else:
                    results.append({
                        'filename': audio_file.name,
                        'transcription': '',
                        'status': 'error',
                        'error': f'HTTP {response.status_code}'
                    })
            
            return JsonResponse({
                'success': True,
                'results': results
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erreur: {str(e)}'
            })
    
    return render(request, 'core/test_batch.html') 