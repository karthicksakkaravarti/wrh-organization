import traceback
from datetime import datetime

import requests
from django.core.management import BaseCommand
from apps.usacycling import models


class Command(BaseCommand):

    def handle(self, *args, **options):
        res = requests.get('https://laravel-api.usacycling.org/api/v1/club_search/1/')
        if not res.ok:
            res.raise_for_status()
        data = res.json()
        for r in data:
            try:
                club_teams = r.pop('club_teams', [])
                club_id = r.pop('club_id')
                club, _ = models.USACClub.objects.update_or_create(club_id=club_id, defaults=r)
                try:
                    for club_team in club_teams:
                        team_id = club_team.pop('team_id')
                        team, _ = models.USACClubTeam.objects.update_or_create(team_id=team_id, defaults=club_team)
                        club.club_teams.add(team)
                except Exception as e:
                    traceback.print_exc()
                # club.save()

            except Exception as e:
                traceback.print_exc()

