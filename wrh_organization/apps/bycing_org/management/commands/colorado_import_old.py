import argparse
import json
import traceback
from datetime import datetime

from django.core.management import BaseCommand
from backports.zoneinfo import ZoneInfo
from django.db import transaction
from django.utils.dateparse import parse_date

from apps.bycing_org.models import Member, Organization, OrganizationMember, Event

tzinfo = ZoneInfo("America/Denver")


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-i', '--input-file', type=argparse.FileType('r'), help='Input json file', required=True)
        parser.add_argument('--orgid', type=int, help='Colorado org id', required=True)
        parser.add_argument('--members', action='store_true', help='import members')
        parser.add_argument('--events', action='store_true', help='import events')
        parser.add_argument('--results', action='store_true', help='import results')

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
        if birth_date:
            birth_date = parse_date(birth_date)
        phone = r.get('phoneCell') or r.get('phoneWork') or r.get('phoneHome') or None
        member = Member.objects.create(
            email=(r.get('email') or '').lower() or None,
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
        OrganizationMember.objects.create(organization=org, member=member, org_member_uid=uid, member_fields=r)
        return member

    @transaction.atomic()
    def _add_event(self, r, org):
        rid = r.get('id')
        if not rid:
            print('[No ID!]')
            return
        start_date = datetime.fromtimestamp(r.get('eventDate')).date()
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
    def _add_result(self, r, org, events_map, riders_map):
        rid = r.get('id')
        if not rid:
            print('[No ID!]')
            return
        start_date = datetime.fromtimestamp(r.get('eventDate')).date()
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

    def import_members(self, file_in, org):
        records = json.load(file_in)
        for i in range(len(records)):
            record = records[i]
            uid = record.get('id')
            print(f'+++ processing user #{i}: id# {uid} ...')
            try:
                self._add_member(record, org)
            except Exception as e:
                traceback.print_exc()

    def import_events(self, file_in, org):
        records = json.load(file_in)
        for i in range(len(records)):
            record = records[i]
            rid = record.get('id')
            print(f'+++ processing event #{i}: id# {rid} ...')
            try:
                self._add_event(record, org)
            except Exception as e:
                traceback.print_exc()

    def import_results(self, file_in, org):
        records = json.load(file_in)
        events_map = {r.more_data['id']: r.id for r in Event.objects.exclude(more_data__id__isnull=True).all()}
        riders_map = {r.member_fields['id']: r.member_id for r in
                      OrganizationMember.objects.filter(organization=org, member_fields__id__isnull=False).all()}
        for i in range(len(records)):
            record = records[i]
            rid = record.get('id')
            print(f'+++ processing result #{i}: id# {rid} ...')
            try:
                self._add_result(record, org, events_map, riders_map)
            except Exception as e:
                traceback.print_exc()

    def handle(self, *args, **options):
        file_in = options.get('input_file')
        org = Organization.objects.get(pk=options.get('orgid'))

        if options.get('users'):
            self.import_members(file_in, org)
        elif options.get('events'):
            self.import_events(file_in, org)
        else:
            self.stderr.write('Insufficent args!\nuse --help for more info')
