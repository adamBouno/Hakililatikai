from django.core.management.base import BaseCommand
from core.models import Article
from django.core.files import File
import os
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class Command(BaseCommand):
    help = 'Crée des articles de test pour la base de données'

    def handle(self, *args, **options):
        # Supprimer les articles existants
        Article.objects.all().delete()
        
        # Articles de test
        articles_data = [
            {
                'titre': 'Prévenir le paludisme',
                'categorie': 'PREV',
                'contenu': '''Le paludisme est une maladie grave transmise par les moustiques. Voici comment vous protéger :

1. Dormez sous une moustiquaire imprégnée
2. Utilisez des répulsifs anti-moustiques
3. Portez des vêtements longs le soir
4. Éliminez les eaux stagnantes autour de votre maison
5. Consultez rapidement en cas de fièvre

Les symptômes incluent fièvre, maux de tête, fatigue et frissons. Un traitement précoce est essentiel.''',
                'auteur': 'Dr. Diallo',
                'mots_cles': 'paludisme, prévention, moustiquaire, fièvre'
            },
            {
                'titre': 'Reconnaître l\'anémie',
                'categorie': 'SYMP',
                'contenu': '''L'anémie se caractérise par un manque de globules rouges. Les signes à surveiller :

Symptômes principaux :
- Fatigue excessive
- Pâleur de la peau
- Essoufflement
- Vertiges
- Palpitations

Causes courantes :
- Carence en fer
- Paludisme chronique
- Malnutrition
- Parasites intestinaux

Traitement : alimentation riche en fer, suppléments si nécessaire, traitement de la cause sous-jacente.''',
                'auteur': 'Dr. Traoré',
                'mots_cles': 'anémie, fatigue, fer, pâleur'
            },
            {
                'titre': 'Fièvre chez l\'enfant',
                'categorie': 'URG',
                'contenu': '''La fièvre chez l'enfant nécessite une attention particulière :

Température normale : 36-37°C
Fièvre : au-dessus de 38°C

Que faire :
1. Prendre la température
2. Donner du paracétamol si > 38.5°C
3. Faire boire beaucoup d'eau
4. Surveiller les autres symptômes

URGENCE si :
- Fièvre > 40°C
- Convulsions
- Raideur de la nuque
- Taches sur la peau
- Enfant très abattu

Consultez immédiatement un médecin dans ces cas.''',
                'auteur': 'Dr. Koné',
                'mots_cles': 'fièvre, enfant, urgence, température'
            },
            {
                'titre': 'Vaccinations essentielles',
                'categorie': 'PREV',
                'contenu': '''Les vaccinations protègent contre les maladies graves :

Calendrier vaccinal :
- BCG : à la naissance
- DTC : 2, 3, 4 mois
- Rougeole : 9 mois
- Fièvre jaune : 9 mois
- Méningite : selon calendrier

Vaccins pour adultes :
- Tétanos : rappel tous les 10 ans
- Fièvre jaune : si voyage
- Hépatite B : selon risque

Les vaccins sont gratuits dans les centres de santé publics.''',
                'auteur': 'Dr. Diarra',
                'mots_cles': 'vaccination, prévention, calendrier, BCG'
            },
            {
                'titre': 'Diabète : surveiller sa glycémie',
                'categorie': 'TRAIT',
                'contenu': '''Le diabète nécessite un suivi régulier :

Surveillance quotidienne :
- Mesurer la glycémie
- Contrôler l'alimentation
- Faire de l'exercice
- Prendre ses médicaments

Signes d'alerte :
- Soif excessive
- Fatigue
- Vision trouble
- Cicatrisation lente

Complications à éviter :
- Problèmes cardiaques
- Cécité
- Amputation

Consultez régulièrement votre médecin.''',
                'auteur': 'Dr. Keita',
                'mots_cles': 'diabète, glycémie, surveillance, complications'
            },
            {
                'titre': 'Hypertension : bons réflexes',
                'categorie': 'TRAIT',
                'contenu': '''L'hypertension artérielle est silencieuse mais dangereuse :

Mesures préventives :
- Réduire le sel
- Faire de l'exercice
- Perdre du poids si nécessaire
- Éviter l'alcool et le tabac
- Gérer le stress

Alimentation recommandée :
- Fruits et légumes
- Céréales complètes
- Poisson maigre
- Limiter les graisses

Surveillance :
- Mesurer la tension régulièrement
- Prendre ses médicaments
- Consulter le médecin''',
                'auteur': 'Dr. Coulibaly',
                'mots_cles': 'hypertension, tension, sel, exercice'
            },
            {
                'titre': 'Grossesse : signaux d\'alerte',
                'categorie': 'URG',
                'contenu': '''Pendant la grossesse, certains symptômes nécessitent une consultation urgente :

URGENCES :
- Saignements vaginaux
- Douleurs abdominales intenses
- Maux de tête sévères
- Troubles de la vision
- Gonflement soudain
- Fièvre élevée

Consultation rapide si :
- Mouvements du bébé diminués
- Contractions avant 37 semaines
- Perte de liquide amniotique

Suivi régulier :
- Consultations prénatales
- Échographies
- Analyses sanguines''',
                'auteur': 'Dr. Sanogo',
                'mots_cles': 'grossesse, urgence, saignement, consultation'
            },
            {
                'titre': 'Déshydratation : réagir vite',
                'categorie': 'URG',
                'contenu': '''La déshydratation peut être grave, surtout chez les enfants :

Signes de déshydratation :
- Soif intense
- Bouche sèche
- Urines foncées
- Fatigue
- Yeux creux (chez l'enfant)

Traitement :
- Boire beaucoup d'eau
- Solution de réhydratation (ORS)
- Repos
- Alimentation légère

Préparation ORS maison :
- 1 litre d'eau bouillie
- 6 cuillères à café de sucre
- 1/2 cuillère à café de sel

URGENCE si :
- Vomissements persistants
- Diarrhée sévère
- Enfant très abattu''',
                'auteur': 'Dr. Ouattara',
                'mots_cles': 'déshydratation, ORS, urgence, eau'
            }
        ]
        
        # Créer les articles
        for i, data in enumerate(articles_data, 1):
            # Utiliser une image existante si disponible
            image_path = f'core/static/core/images/carte{i}.png'
            if os.path.exists(image_path):
                with open(image_path, 'rb') as img_file:
                    article = Article.objects.create(
                        titre=data['titre'],
                        categorie=data['categorie'],
                        contenu=data['contenu'],
                        auteur=data['auteur'],
                        mots_cles=data['mots_cles']
                    )
                    article.image.save(f'carte{i}.png', File(img_file), save=True)
            else:
                # Créer sans image si le fichier n'existe pas
                article = Article.objects.create(
                    titre=data['titre'],
                    categorie=data['categorie'],
                    contenu=data['contenu'],
                    auteur=data['auteur'],
                    mots_cles=data['mots_cles']
                )
            
            self.stdout.write(
                self.style.SUCCESS(f'Article créé : {article.titre}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'{len(articles_data)} articles créés avec succès!')
        ) 

        try:
            user = User.objects.get(username='kampo')
            print(f"Utilisateur trouvé: {user.username}")
            print(f"Email: {user.email}")
            print(f"Superutilisateur: {user.is_superuser}")
            print(f"Actif: {user.is_active}")
            print(f"Dernière connexion: {user.last_login}")
        except User.DoesNotExist:
            print("L'utilisateur 'kampo' n'existe pas!") 

        user = authenticate(username='kampo', password='DjangoR@ssure2023')
        if user:
            print("✅ Authentification réussie!")
            print(f"Utilisateur: {user.username}")
            print(f"Actif: {user.is_active}")
        else:
            print("❌ Échec de l'authentification")

        user = User.objects.get(username='kampo')
        if not user.is_active:
            user.is_active = True
            user.save()
            print("✅ Utilisateur activé!")
        else:
            print("✅ Utilisateur déjà actif")

        user = User.objects.get(username='kampo')
        user.set_password('DjangoR@ssure2023')
        user.save()
        print("✅ Mot de passe réinitialisé!")

        # Paramètres de session
        SESSION_COOKIE_AGE = 1209600  # 2 semaines
        SESSION_EXPIRE_AT_BROWSER_CLOSE = False
        SESSION_SAVE_EVERY_REQUEST = True

        # Redémarrer le serveur
        # Arrêtez le serveur (Ctrl+C)
        # python manage.py runserver

        # Essayer de se connecter
        # Allez sur `http://127.0.0.1:8000/admin/` et essayez de vous connecter avec :
        # - **Nom d'utilisateur :** `kampo`
        # - **Mot de passe :** `DjangoR@ssure2023`

        # Vérifier les logs du serveur quand vous essayez de vous connecter. Vous devriez voir :
        # ```
        # [timestamp] "POST /admin/login/ HTTP/1.1" 302 0
        # ```

        # Si vous voyez `200` au lieu de `302`, cela confirme que la connexion échoue.

        # **Commencez par l'étape 1 pour vérifier l'état de votre utilisateur, puis suivez les étapes selon ce que vous trouvez.**

        # Dites-moi ce que vous obtenez à l'étape 1 et 2, et je vous guiderai pour la suite ! 