from django.core.management.base import BaseCommand
from core.models import CentreMedical
import math

class Command(BaseCommand):
    help = 'Ajoute tous les centres médicaux de Bamako'

    def handle(self, *args, **options):
        # Supprimer tous les centres existants
        CentreMedical.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Centres existants supprimés'))
        
        # Liste complète des centres
        centres_data = [
            # Hôpitaux (HP)
            {
                'nom': 'Hôpital du Point G',
                'type': 'HP',
                'adresse': 'Bamako, Point G',
                'telephone': '+223 20 22 37 37',
                'latitude': 12.6300,
                'longitude': -7.9900,
                'services': 'Hôpital universitaire, Urgences, Chirurgie, Maternité, Pédiatrie'
            },
            {
                'nom': 'Hôpital Gabriel Touré',
                'type': 'HP',
                'adresse': 'Bamako, Hamdallaye ACI',
                'telephone': '+223 20 22 37 37',
                'latitude': 12.6512,
                'longitude': -8.0123,
                'services': 'Urgences, Consultations, Laboratoire, Imagerie'
            },
            {
                'nom': 'Hôpital Mère-Enfant',
                'type': 'HP',
                'adresse': 'Bamako, Faladié',
                'telephone': '+223 20 22 37 37',
                'latitude': 12.6450,
                'longitude': -7.9850,
                'services': 'Maternité, Pédiatrie, Gynécologie, Urgences'
            },
            {
                'nom': 'Hôpital National',
                'type': 'HP',
                'adresse': 'Bamako, Quartier du Fleuve',
                'telephone': '+223 20 22 37 37',
                'latitude': 12.6350,
                'longitude': -7.9950,
                'services': 'Urgences, Chirurgie, Médecine interne, Spécialités'
            },
            
            # Cliniques (CL)
            {
                'nom': 'Clinique Pasteur',
                'type': 'CL',
                'adresse': 'Bamako, Hamdallaye ACI',
                'telephone': '+223 20 22 37 37',
                'latitude': 12.6512,
                'longitude': -8.0123,
                'services': 'Consultations, Laboratoire, Vaccination, Médecine générale'
            },
            {
                'nom': 'Clinique Golden Life',
                'type': 'CL',
                'adresse': 'Bamako, ACI 2000',
                'telephone': '+223 20 22 37 37',
                'latitude': 12.6392,
                'longitude': -8.0029,
                'services': 'Consultations, Imagerie, Médecine générale, Spécialités'
            },
            {
                'nom': 'Clinique Médicale du Mali',
                'type': 'CL',
                'adresse': 'Bamako, Badalabougou',
                'telephone': '+223 20 22 37 37',
                'latitude': 12.6400,
                'longitude': -8.0000,
                'services': 'Consultations, Laboratoire, Médecine générale'
            },
            {
                'nom': 'Clinique Farako',
                'type': 'CL',
                'adresse': 'Bamako, Farako',
                'telephone': '+223 20 22 37 37',
                'latitude': 12.6480,
                'longitude': -8.0080,
                'services': 'Consultations, Médecine générale, Pédiatrie'
            },
            {
                'nom': 'Clinique Médicale de l\'ACI',
                'type': 'CL',
                'adresse': 'Bamako, ACI 2000',
                'telephone': '+223 20 22 37 37',
                'latitude': 12.6420,
                'longitude': -8.0050,
                'services': 'Consultations, Laboratoire, Médecine générale'
            },
            {
                'nom': 'Clinique Médicale de Badalabougou',
                'type': 'CL',
                'adresse': 'Bamako, Badalabougou',
                'telephone': '+223 20 22 37 37',
                'latitude': 12.6380,
                'longitude': -7.9980,
                'services': 'Consultations, Médecine générale, Pédiatrie'
            },
            {
                'nom': 'Centre Médical de Sotuba',
                'type': 'CL',
                'adresse': 'Bamako, Sotuba',
                'telephone': '+223 20 22 37 37',
                'latitude': 12.6550,
                'longitude': -7.9750,
                'services': 'Consultations, Médecine générale, Pédiatrie'
            },
            {
                'nom': 'Centre Médical de Kalaban',
                'type': 'CL',
                'adresse': 'Bamako, Kalaban',
                'telephone': '+223 20 22 37 37',
                'latitude': 12.6600,
                'longitude': -7.9700,
                'services': 'Consultations, Médecine générale'
            },
            {
                'nom': 'Centre Médical de Niamakoro',
                'type': 'CL',
                'adresse': 'Bamako, Niamakoro',
                'telephone': '+223 20 22 37 37',
                'latitude': 12.6450,
                'longitude': -7.9750,
                'services': 'Consultations, Médecine générale, Pédiatrie'
            },
            {
                'nom': 'Centre Médical de Lafiabougou',
                'type': 'CL',
                'adresse': 'Bamako, Lafiabougou',
                'telephone': '+223 20 22 37 37',
                'latitude': 12.6350,
                'longitude': -7.9800,
                'services': 'Consultations, Médecine générale'
            },
            {
                'nom': 'Centre Médical de Médina',
                'type': 'CL',
                'adresse': 'Bamako, Médina',
                'telephone': '+223 20 22 37 37',
                'latitude': 12.6500,
                'longitude': -7.9900,
                'services': 'Consultations, Médecine générale, Pédiatrie'
            },
            
            # Centres d'Urgences (UR)
            {
                'nom': 'Centre d\'Urgences Médicales',
                'type': 'UR',
                'adresse': 'Bamako, Centre-ville',
                'telephone': '+223 20 22 37 37',
                'latitude': 12.6500,
                'longitude': -8.0000,
                'services': 'Urgences 24/7, SAMU, Réanimation'
            },
            {
                'nom': 'Centre d\'Urgences de l\'ACI',
                'type': 'UR',
                'adresse': 'Bamako, ACI 2000',
                'telephone': '+223 20 22 37 37',
                'latitude': 12.6410,
                'longitude': -8.0030,
                'services': 'Urgences, Ambulance, Premiers soins'
            },
            {
                'nom': 'Centre d\'Urgences de Hamdallaye',
                'type': 'UR',
                'adresse': 'Bamako, Hamdallaye',
                'telephone': '+223 20 22 37 37',
                'latitude': 12.6520,
                'longitude': -8.0130,
                'services': 'Urgences, SAMU, Réanimation'
            },
            {
                'nom': 'Centre d\'Urgences de Faladié',
                'type': 'UR',
                'adresse': 'Bamako, Faladié',
                'telephone': '+223 20 22 37 37',
                'latitude': 12.6460,
                'longitude': -7.9860,
                'services': 'Urgences, Ambulance, Premiers soins'
            },
            {
                'nom': 'Centre d\'Urgences de Badalabougou',
                'type': 'UR',
                'adresse': 'Bamako, Badalabougou',
                'telephone': '+223 20 22 37 37',
                'latitude': 12.6390,
                'longitude': -7.9970,
                'services': 'Urgences, SAMU, Réanimation'
            },
        ]
        
        # Créer tous les centres
        centres_created = []
        for centre_data in centres_data:
            centre = CentreMedical.objects.create(**centre_data)
            centres_created.append(centre)
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ {len(centres_created)} centres médicaux ajoutés avec succès !')
        )
        
        # Afficher un résumé
        by_type = {}
        for centre in centres_created:
            if centre.type not in by_type:
                by_type[centre.type] = 0
            by_type[centre.type] += 1
        
        self.stdout.write('\n📊 Répartition par type :')
        for type_centre, count in by_type.items():
            type_name = {'HP': 'Hôpitaux', 'CL': 'Cliniques', 'UR': 'Centres d\'Urgences'}[type_centre]
            self.stdout.write(f'   • {type_name}: {count} centres')
        
        self.stdout.write('\n🎯 Pour voir les centres, va sur la page /centres/') 