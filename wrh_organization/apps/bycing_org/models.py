from pathlib import Path

from cerberus import Validator
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from model_utils import FieldTracker
from phonenumber_field.modelfields import PhoneNumberField

from apps.usacycling.models import USACEvent
from wrh_organization.helpers.fields_tracking import BaseFieldsTracking

User = get_user_model()


def organization_logo_file_path_func(instance, filename):
    from wrh_organization.helpers.utils import get_random_upload_path
    return get_random_upload_path(str(Path('uploads', 'bycing_org', 'organization', 'logo')), filename)


class FieldsTracking(BaseFieldsTracking):
    pass


@FieldsTracking.register()
class OrganizationMember(models.Model):
    STATUS_ACCEPT = 'accept'
    STATUS_REJECT = 'reject'
    STATUS_WAITING = 'waiting'
    STATUS_CHOICES = (
        (STATUS_ACCEPT, 'Accept'),
        (STATUS_REJECT, 'Reject'),
        (STATUS_WAITING, 'Waiting'),
    )
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE)
    member = models.ForeignKey('Member', on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    is_master_admin = models.BooleanField(default=False)
    membership_price = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    is_active = models.BooleanField(default=True, null=True)
    org_member_uid = models.CharField(max_length=256, null=True, blank=True)
    start_date = models.DateField(null=True)
    exp_date = models.DateField(null=True)
    member_fields = models.JSONField(null=True)
    status = models.CharField(max_length=16, null=True, choices=STATUS_CHOICES)
    datetime = models.DateTimeField(auto_now_add=True)
    _tracker = FieldTracker()

    class Meta:
        unique_together = (
            ('organization', 'member', 'is_active'),
            ('organization', 'org_member_uid', 'is_active')
        )

    def jsonify_entry_form(self):
        for f in (self.organization.member_fields_schema or []):
            name = f['name']
            value = self.member_fields.get(name)
            if not value:
                continue
            if f['type'] == 'time':
                self.member_fields[name] = value.strftime('%H:%M:%S')
            elif f['type'] == 'date':
                self.member_fields[name] = value.strftime('%Y-%m-%d')
            elif f['type'] == 'datetime':
                self.member_fields[name] = value.isoformat()

    def save(self, *args, **kwargs):
        if not self.is_active:
            self.is_active = None
        if not self.org_member_uid:
            self.org_member_uid = None
        if self.is_master_admin:
            self.is_admin = True
        if self.member_fields:
            v = Validator(self.organization.normalized_member_fields_schema, allow_unknown=True)
            if not v.validate(self.member_fields or {}):
                raise ValidationError({'member_fields': str(v.errors)})
            self.member_fields = v.document
            self.jsonify_entry_form()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.organization} - {self.member}'


@FieldsTracking.register()
class OrganizationMemberOrg(models.Model):
    STATUS_ACCEPT = 'accept'
    STATUS_REJECT = 'reject'
    STATUS_WAITING = 'waiting'
    STATUS_CHOICES = (
        (STATUS_ACCEPT, 'Accept'),
        (STATUS_REJECT, 'Reject'),
        (STATUS_WAITING, 'Waiting'),
    )
    organization = models.ForeignKey('Organization', related_name='organizaton_member_orgs',
                                     on_delete=models.CASCADE)
    member_org = models.ForeignKey('Organization', related_name='member_organizaton_member_orgs',
                                   on_delete=models.CASCADE)
    membership_price = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    is_active = models.BooleanField(default=True, null=True)
    start_date = models.DateField(null=True)
    exp_date = models.DateField(null=True)
    member_fields = models.JSONField(null=True)
    status = models.CharField(max_length=16, null=True, choices=STATUS_CHOICES)
    datetime = models.DateTimeField(auto_now_add=True)
    _tracker = FieldTracker()

    class Meta:
        unique_together = (('organization', 'member_org', 'is_active'),)

    def save(self, *args, **kwargs):
        if not self.is_active:
            self.is_active = None
        org_id = (self.organization and self.organization.id) or self.organization_id
        member_org_id = (self.member_org and self.member_org.id) or self.member_org_id
        if org_id == member_org_id:
            raise ValidationError({"member_org": "member_org cannot be same as organization"})
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.organization} - {self.member_org}'


@FieldsTracking.register()
class Organization(models.Model):
    MEMBER_FIELDS_SCHEMA_VALIDATOR = {
        'type': 'list', 'empty': True, 'required': False,
        'schema': {
            'type': 'dict', 'schema': {
                'name': {'type': 'string', 'required': True, 'nullable': False, 'empty': False},
                'title': {'type': 'string', 'required': True, 'nullable': False, 'empty': False},
                'type': {
                    'type': 'string', 'required': True, 'nullable': False, 'empty': False,
                    'allowed': [
                        'integer', 'float', 'number', 'string', 'text', 'boolean', 'percent', 'date', 'time', 'datetime'
                    ]
                },
                'required': {'type': 'boolean', 'required': False, 'default': False},
                'choices': {
                    'type': 'list', 'required': False, 'nullable': True, 'empty': True,
                    'schema': {
                        'type': 'dict', 'empty': False,
                        'schema': {'title': {'type': 'string'}, 'value': {}}
                    }
                },
                'multiple': {'type': 'boolean', 'required': False, 'default': False},
            }
        },
    }

    TYPE_REGIONAL = 'regional'
    TYPE_TEAM = 'team'
    TYPE_ADVOCACY_VOLUNTEER = 'advocacy_volunteer'
    TYPE_CHOICES = (
        (TYPE_REGIONAL, 'Regional'),
        (TYPE_TEAM, 'Team'),
        (TYPE_ADVOCACY_VOLUNTEER, 'Advocacy, Volunteer'),
    )
    name = models.CharField(max_length=256, unique=True)
    type = models.CharField(max_length=32, choices=TYPE_CHOICES)
    social_media = models.JSONField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    phone = PhoneNumberField(max_length=50, null=True, blank=True)
    phone_verified = models.BooleanField(default=None, null=True)
    email = models.EmailField(null=True, blank=True)
    email_verified = models.BooleanField(default=None, null=True)
    address = models.CharField(max_length=256, blank=True, null=True)
    country = models.CharField(max_length=128, blank=True, null=True)
    city = models.CharField(max_length=128, blank=True, null=True)
    state = models.CharField(max_length=128, blank=True, null=True)
    zipcode = models.CharField(max_length=10, blank=True, null=True)
    about = models.TextField(null=True, blank=True)
    logo = models.ImageField(null=True, blank=True, upload_to=organization_logo_file_path_func)
    signup_config = models.JSONField(null=True)
    member_fields_schema = models.JSONField(null=True)
    verified = models.BooleanField(default=False)
    members = models.ManyToManyField('Member', related_name='organizations', through=OrganizationMember)
    member_orgs = models.ManyToManyField('Organization', related_name='organizations', through=OrganizationMemberOrg)
    _tracker = FieldTracker()

    @property
    def normalized_member_fields_schema(self):
        from wrh_organization.helpers.utils import (date_coerce, time_coerce, datetime_coerce, float_safe_coerce,
                                                    number_safe_coerce, integer_safe_coerce)
        coerces = {
            'integer': integer_safe_coerce,
            'float': float_safe_coerce,
            'number': number_safe_coerce,
            'date': date_coerce,
            'time': time_coerce,
            'datetime': datetime_coerce,
        }
        schema = {}
        for f in (self.member_fields_schema or []):
            d = dict(type=f.get('type'))

            # type
            if d['type'] == 'percent':
                d['type'] = 'integer'
                d['min'] = 0
                d['max'] = 100
            elif d['type'] == 'text':
                d['type'] = 'string'
            if d['type'] in coerces:
                d['coerce'] = coerces[d['type']]

            # required
            required = f.get('required') is True
            d['required'] = required
            d['nullable'] = not required
            d['empty'] = not required

            # choices
            choices = f.get('choices')
            if choices:
                d['allowed'] = [c.get('value') for c in choices]
            if f.get('multiple'):
                schema[f['name']] = {
                    'type': 'list', 'schema': d, 'required': required, 'nullable': not required, 'empty': not required
                }
            else:
                schema[f['name']] = d

        return schema

    def save(self, *args, **kwargs):
        if self.member_fields_schema:
            v = Validator({'member_fields_schema': self.MEMBER_FIELDS_SCHEMA_VALIDATOR}, purge_unknown=True)
            if not v.validate({'member_fields_schema': self.member_fields_schema}):
                raise ValidationError({'member_fields_schema': str(v.errors)})
            self.member_fields_schema = v.document['member_fields_schema']
        else:
            self.member_fields_schema = []
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}'


class Member(models.Model):
    SOCIAL_MEDIA_SCHEMA = {
        'zwift': {
            'type': 'string', 'required': False, 'nullable': True, 'meta': {'title': 'Zwift'}
        },
        'zwiftpower': {
            'type': 'string', 'required': False, 'nullable': True, 'meta': {'title': 'Zwift Power'}
        },
        'strava': {
            'type': 'string', 'required': False, 'nullable': True, 'meta': {'title': 'Strava'}
        },
        'youtube': {
            'type': 'string', 'required': False, 'nullable': True, 'meta': {'title': 'Youtube'}
        },
        'facebook': {
            'type': 'string', 'required': False, 'nullable': True, 'meta': {'title': 'Facebook'}
        },
        'instagram': {
            'type': 'string', 'required': False, 'nullable': True, 'meta': {'title': 'Instagram'}
        },
    }

    USER_SHARED_FIELDS = ('first_name', 'last_name', 'birth_date', 'gender')

    GENDER_MALE = 'm'
    GENDER_FEMALE = 'f'
    GENDER_OTHER = 'o'
    GENDER_UNKNOWN = 'u'
    GENDER_CHOICES = (
        (GENDER_MALE, 'Male'),
        (GENDER_FEMALE, 'Female'),
        (GENDER_OTHER, 'Other'),
        (GENDER_UNKNOWN, 'Unknown'),
    )
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default=GENDER_UNKNOWN)
    birth_date = models.DateField(null=True, blank=True)
    phone = PhoneNumberField(max_length=50, null=True, blank=True)
    phone_verified = models.BooleanField(default=None, null=True)
    email = models.EmailField(null=True, blank=True)
    email_verified = models.BooleanField(default=None, null=True)
    address1 = models.CharField(max_length=256, blank=True, null=True)
    address2 = models.CharField(max_length=256, blank=True, null=True)
    country = models.CharField(max_length=128, blank=True, null=True)
    city = models.CharField(max_length=128, blank=True, null=True)
    state = models.CharField(max_length=128, blank=True, null=True)
    zipcode = models.CharField(max_length=10, blank=True, null=True)
    weight = models.DecimalField('Weight (kg)', max_digits=5, decimal_places=2, null=True, blank=True,
                                 validators=[MinValueValidator(10), MaxValueValidator(300)])
    height = models.DecimalField('Height (m)', max_digits=3, decimal_places=2, null=True, blank=True,
                                 validators=[MinValueValidator(1), MaxValueValidator(3)])

    social_media = models.JSONField(null=True, blank=True)
    is_verified = models.BooleanField(default=None, null=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, related_name='member', null=True)

    def generate_verify_code(self, type='email'):
        '''
        :param type: can be "email" or "phone"
        :return: str of numbers
        '''
        from wrh_organization.helpers.utils import get_member_verify_otp
        return get_member_verify_otp(self, salt=type).now()

    def check_verify_code(self, code, type='email', valid_window=0):
        '''
        :param code: str of numbers
        :param type: can be "email" or "phone"
        :return: True if verified else False
        '''
        from wrh_organization.helpers.utils import get_member_verify_otp
        return get_member_verify_otp(self, salt=type).verify(code, valid_window=valid_window)

    def save(self, *args, **kwargs):
        if not self.phone:
            self.phone = None
        if not self.email:
            self.email = None
        if not self.email_verified:
            self.email_verified = None
        if not self.phone_verified:
            self.phone_verified = None
        if not self.is_verified:
            self.is_verified = None
        if self.social_media:
            v = Validator(self.SOCIAL_MEDIA_SCHEMA, allow_unknown=True)
            if not v.validate(self.social_media):
                raise ValidationError({'social_media': str(v.errors)})
            self.social_media = v.document
        else:
            self.social_media = {}
        return super().save(*args, **kwargs)

    class Meta:
        unique_together = (('email', 'email_verified'), ('phone', 'phone_verified'),)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Race(models.Model):
    name = models.CharField(max_length=256)
    event = models.ForeignKey(USACEvent, on_delete=models.CASCADE)
    start_datetime = models.DateTimeField()
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, related_name='races')
    create_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    create_datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('name', 'event', 'organization'),)

    def __str__(self):
        return self.name


class RaceResult(models.Model):
    rider = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, related_name='race_results')
    race = models.ForeignKey(Race, on_delete=models.CASCADE)
    place = models.IntegerField(validators=[MinValueValidator(1)])
    more_data = models.JSONField(null=True)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True)
    create_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    create_datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('rider', 'race', 'organization'),)

    def save(self, *args, **kwargs):
        if not self.more_data:
            self.more_data = {}
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.place}-{self.rider}'
