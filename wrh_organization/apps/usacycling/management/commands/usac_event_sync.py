from datetime import datetime

import requests
from django.core.management import BaseCommand
from django.utils import timezone

from apps.bycing_org.models import Event
from apps.bycing_org.rest_api.serializers import EventSerializer
from apps.usacycling.models import USACEvent
import datetime

from apps.usacycling.rest_api.serializers import USACEventSerializer


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
                    ser = USACEventSerializer(instance=instance, data=r)
                    ser.is_valid(raise_exception=True)
                    ser.save()
                except Exception as e:
                    print(f'Exception1: #{r["event"]}', e)

                instance = Event.objects.filter(source='usac', more_data__event_id=r['event_id']).first()
                try:
                    links = (r.get('links') or {})
                    website = links.get('website_url')
                    if website and not website.startswith('http://') and not website.startswith('https://'):
                        website = 'http://' + website
                    registration_website = links.get('register_url')
                    if registration_website and not registration_website.startswith('http://') and not \
                            registration_website.startswith('https://'):
                        registration_website = 'http://' + registration_website
                    tags = (r.get('labels') or []) + (r.get('tags') or [])
                    data = dict(
                        name=r.get('name'), start_date=r.get('start_date'), end_date=r.get('end_date'),
                        organizer_email=r.get('event_organizer_email'), website=website,
                        registration_website=registration_website, tags=tags, country='US',
                        organization=None, more_data=r
                    )
                    ser = EventSerializer(instance=instance, data=data)
                    ser.is_valid(raise_exception=True)
                    ser.save(source='usac')
                except Exception as e:
                    print(f'Exception2: #{r["event"]}', e)
