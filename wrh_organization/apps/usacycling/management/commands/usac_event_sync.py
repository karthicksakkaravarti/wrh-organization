from datetime import datetime

import requests
from django.core.management import BaseCommand
from apps.usacycling import models
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

    def handle(self, *args, **options):
        years = [2021, 2022]
        for year in years:
            for month in range(1, 13):
                try:
                    start_date, end_date = last_day_of_month(datetime.date(year, month, 1))
                    req = requests.get(
                        f'https://laravel-api.usacycling.org/api/v1/event_search?start_date={start_date}&end_date={end_date}')
                    if req.status_code == 200:
                        for i in req.json().get("data"):
                            try:
                                i['dates'] = i['dates'][0]
                                sser = serializers.USAEventSerializer(data=i)
                                sser.is_valid(raise_exception=True)
                                sser.save()
                            except Exception as e:
                                print('Exception',e)
                                continue
                except Exception as e:
                    print("Exception",str(e))


