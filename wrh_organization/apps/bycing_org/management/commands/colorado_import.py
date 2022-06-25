import argparse
import getpass

import mysql.connector
import json
import traceback
from datetime import datetime

from django.core.management import BaseCommand
from backports.zoneinfo import ZoneInfo
from django.db import transaction
from django.utils.dateparse import parse_date
from docutils.nodes import status

from apps.bycing_org.models import Member, Organization, OrganizationMember, Event, RaceResult, Race

tzinfo = ZoneInfo("America/Denver")


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--orgid', type=int, help='Colorado org id', required=True)

        parser.add_argument('--username', type=str, help='mysql username', required=True)
        parser.add_argument('--password', type=str, help='mysql password')
        parser.add_argument('--host', type=str, help='mysql host', default='localhost')
        parser.add_argument('--port', type=int, help='mysql host', default=3306)
        parser.add_argument('--db', type=str, help='mysql database', required=True)

        parser.add_argument('--members', action='store_true', help='import members')
        parser.add_argument('--events', action='store_true', help='import events')
        parser.add_argument('--races', action='store_true', help='import races')
        parser.add_argument('--results', action='store_true', help='import results')

    def json_query(self, cur):
        return [dict(zip(cur.column_names, r)) for r in cur.fetchall()]

    def get_table_cols(self, cur, table):
        cur.execute(f'select * from {table} limit 1')
        cur.fetchall()
        return cur.column_names

    @transaction.atomic()
    def _add_member(self, r, org):
        uid = r.get('id')
        if not uid:
            print('[No ID!]')
            return
        org_member = OrganizationMember.objects.filter(organization=org, org_member_uid=uid, is_active=True).first()
        if org_member:
            print('Member with this licesne already exists!')
            return
        gender = (r.get('gender') or '').lower()
        birth_date = r.get('dob') or None
        if birth_date and isinstance(birth_date, str):
            birth_date = parse_date(birth_date)
        phone = r.get('phoneCell') or r.get('phoneWork') or r.get('phoneHome') or None
        email = (r.get('email') or '').lower() or None,
        member = Member.objects.create(
            email=email,
            phone=phone,
            first_name=r.get('firstName') or None,
            last_name=r.get('lastName') or None,
            gender=gender if gender in ('m', 'f') else Member.GENDER_UNKNOWN,
            birth_date=birth_date,
            address1=r.get('address1') or None,
            address2=r.get('address2') or None,
            city=r.get('city') or None,
            state=r.get('state') or None,
            country='US',
            zipcode=r.get('zip') or None,
            more_data={'imported': True, 'src': 'colorado'}
        )
        r.update({'imported': True, 'src': 'colorado'})
        OrganizationMember.objects.create(organization=org, member=member, org_member_uid=uid, member_fields=r,
                                          status=OrganizationMember.STATUS_WAITING)
        return member

    @transaction.atomic()
    def _add_event(self, r, org):
        rid = r.get('id')
        if not rid:
            print('[No ID!]')
        start_date = datetime.fromtimestamp(r.get('eventDate')).date()
        r['src'] = 'colorado'
        event = Event.objects.update_or_create(more_data__id=rid, more_data__src='colorado', defaults=dict(
            name=r.get('name'),
            description=r.get('description') or None,
            start_date=start_date,
            country='US',
            state=r.get('eventState') or None,
            city=r.get('eventCity') or None,
            more_data=r
        ))
        return event

    @transaction.atomic()
    def _add_result(self, r, org, riders_map, races_map):
        rid = r.get('id')
        if not rid:
            print('[No ID!]')
            return
        r['src'] = 'colorado'
        raid = r.get('racerId')
        if not raid:
            print('[No Racer ID!]')
            return
        rider_id = riders_map.get(raid)
        if not rider_id:
            print('[No Rider!]')
            return
        ergid = r.get('eventRaceGroupId')
        eid = r.get('eventId')
        race_id = races_map.get((eid, ergid))
        if not race_id:
            print('[No Race!]')
            return

        result = RaceResult.objects.update_or_create(more_data__id=rid, more_data__src='colorado', defaults=dict(
            rider_id=rider_id,
            race_id=race_id,
            place=r.get('place') or None,
            organization=org,
            more_data=r
        ))
        return result

    @transaction.atomic()
    def _add_race(self, r, org, events_map):
        rid = r.get('id')
        if not rid:
            print('[No ID!]')
            return
        eid = r.get('eventId')
        if not eid:
            print('[No Event ID!]')
            return
        event_id = events_map.get(eid)
        if not event_id:
            print('[No Event!]')
            return
        r['src'] = 'colorado'
        race = Race.objects.update_or_create(more_data__id=rid, organization=org,
                                             more_data__src='colorado', defaults=dict(
                name=r.get('name'),
                event_id=event_id,
                organization=org,
                more_data=r,
            ))
        return race

    def import_members(self, conn, org):
        cur = conn.cursor()
        cur.execute('select * from aca_user')
        records = self.json_query(cur)
        for i in range(len(records)):
            record = records[i]
            uid = record.get('id')
            print(f'+++ processing user #{i}: id# {uid} ...')
            try:
                self._add_member(record, org)
            except Exception as e:
                traceback.print_exc()

    def import_events(self, conn, org):
        cur = conn.cursor()
        cur.execute('select * from aca_event')
        records = self.json_query(cur)

        for i in range(len(records)):
            record = records[i]
            rid = record.get('id')
            print(f'+++ processing event #{i}: id# {rid} ...')
            try:
                self._add_event(record, org)
            except Exception as e:
                traceback.print_exc()

    def import_races(self, conn, org):
        cur = conn.cursor()
        cols = list(filter(lambda c: c not in ['id'], self.get_table_cols(cur, 'aca_racegroup')))
        cols = ', '.join([f'aca_racegroup.{c}' for c in cols])
        q = f'select aca_eventracegroup.id, aca_eventracegroup.eventId, aca_racegroup.id as raceId, ' \
            f'{cols} from aca_eventracegroup inner join aca_racegroup on ' \
            f'aca_racegroup.id = aca_eventracegroup.raceGroupId where aca_eventracegroup.eventId is not NULL ' \
            f'and aca_eventracegroup.raceGroupId is not NULL '
        cur.execute(q)
        records = self.json_query(cur)
        events_map = {r.more_data['id']: r.id for r in Event.objects.filter(more_data__id__isnull=False).all()}
        for i in range(len(records)):
            record = records[i]
            rid = record.get('id')
            print(f'+++ processing race #{i}: id# {rid} ...')
            try:
                self._add_race(record, org, events_map)
            except Exception as e:
                traceback.print_exc()

    def import_results(self, conn, org):
        cur = conn.cursor()
        cur.execute('select * from aca_result where '
                    'eventRaceGroupId is not NULL and racerId is not NULL and eventId is not NULL')
        records = self.json_query(cur)
        riders_map = {r.member_fields['id']: r.member_id for r in
                      OrganizationMember.objects.filter(organization=org, member_fields__id__isnull=False).all()}
        races_map = {(r.more_data['eventId'], r.more_data['raceId']): r.id for r in
                      Race.objects.filter(organization=org, more_data__eventId__isnull=False,
                                          more_data__raceId__isnull=False).all()}
        for i in range(len(records)):
            record = records[i]
            rid = record.get('id')
            print(f'+++ processing result #{i}: id# {rid} ...')
            try:
                self._add_result(record, org, riders_map, races_map)
            except Exception as e:
                traceback.print_exc()

    def handle(self, *args, **options):
        org = Organization.objects.get(pk=options.get('orgid'))
        if not options.get('password'):
            options['password'] = getpass.getpass('Enter Database Password: ')

        conn = mysql.connector.connect(user=options.get('username'), password=options.get('password'),
                                      host=options.get('host'),
                                      database=options.get('db'))
        try:
            if options.get('members'):
                self.import_members(conn, org)
            if options.get('events'):
                self.import_events(conn, org)
            if options.get('races'):
                self.import_races(conn, org)
            if options.get('results'):
                self.import_results(conn, org)
        finally:
            conn.close()
