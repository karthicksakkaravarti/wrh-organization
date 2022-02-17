from datetime import datetime

import requests
from django.core.management import BaseCommand
from apps.usacycling import models


class Command(BaseCommand):

    def handle(self, *args, **options):
        req = requests.get('https://laravel-api.usacycling.org/api/v1/club_search/1/')
        models.USACyclingClubs.objects.all().delete()
        models.USACyclingClubTeams.objects.all().delete()
        if req.status_code == 200:
            for i in req.json():
                try:
                    clubteamSource = i.pop('club_teams', [])
                    club = models.USACyclingClubs.objects.get_or_create(**i)[0]
                    try:
                        for clubteams in  clubteamSource:
                            club.club_teams.add(models.USACyclingClubTeams.objects.get_or_create(**clubteams)[0])
                    except Exception as e:
                        print("Exception:", str(e))
                    club.save()

                except Exception as e:
                    print(e)
                    continue

