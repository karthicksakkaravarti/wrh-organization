from datetime import datetime

import requests
from django.core.management import BaseCommand
from django.utils import timezone

from apps.usacycling import models
from apps.usacycling.models import USACEvent
from apps.usacycling.rest_api import serializers
import datetime

def last_day_of_month(any_day):
    try:
        # this will never fail
        # get close to the end of the month for any day, and add 4 days 'over'
        next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
        # subtract the number of remaining 'overage' days to get last day of current month, or said programattically said, the previous day of the first of next month
        return any_day, next_month - datetime.timedelta(days=next_month.day)
    except Exception as e:
        print("Excepton", str(e))


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('years', nargs='*', type=int, help='list of years')

    def handle(self, *args, **options):
        years = options.get('years')
        if not years:
            years = [timezone.now().year]
        for year in years:
            start_date = datetime.date(year, 1, 1)
            end_date = start_date.replace(year=year + 1) - datetime.timedelta(days=1)
            res = requests.get(
                f'https://laravel-api.usacycling.org/api/v1/event_search?start_date={start_date}&end_date={end_date}')
            if not res.ok:
                res.raise_for_status()
            data = res.json().get("data") or []
            for r in data:
                instance = USACEvent.objects.filter(event_id=r['event_id']).first()
                try:
                    sser = serializers.USACEventSerializer(instance=instance, data=r)
                    sser.is_valid(raise_exception=True)
                    sser.save()
                except Exception as e:
                    print('Exception',e)
