from pathlib import Path

from django.contrib.auth import get_user_model
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

User = get_user_model()

def organization_logo_file_path_func(instance, filename):
    from wrh_organization.helpers.utils import get_random_upload_path
    return get_random_upload_path(str(Path('uploads', 'bycing_org', 'organization', 'logo')), filename)


class OrganizationMember(models.Model):
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE)
    member = models.ForeignKey('Member', on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    is_master_admin = models.BooleanField(default=False)
    membership_price = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    member_fields = models.JSONField(null=True)
    is_active = models.BooleanField(default=True, null=True)
    datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('organization', 'member', 'is_active'),)

    def save(self, *args, **kwargs):
        if not self.is_active:
            self.is_active = None
        if self.is_master_admin:
            self.is_admin = True
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.organization} - {self.member}'


class OrganizationMemberOrg(models.Model):
    organization = models.ForeignKey('Organization', related_name='organizaton_member_orgs', on_delete=models.CASCADE)
    top_organization = models.ForeignKey('Organization', related_name='top_organizaton_member_orgs',
                                         on_delete=models.CASCADE)
    membership_price = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    is_active = models.BooleanField(default=True, null=True)
    datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('organization', 'top_organization', 'is_active'),)

    def save(self, *args, **kwargs):
        if not self.is_active:
            self.is_active = None
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.top_organization} - {self.organization}'


class Organization(models.Model):
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
    about = models.TextField(null=True, blank=True)
    logo = models.ImageField(null=True, blank=True, upload_to=organization_logo_file_path_func)
    signup_config = models.JSONField(null=True)
    member_fields_schema = models.JSONField(null=True)
    verified = models.BooleanField(default=False)
    members = models.ManyToManyField('Member', related_name='organizations', through=OrganizationMember)
    member_orgs = models.ManyToManyField('Organization', related_name='organizations', through=OrganizationMemberOrg)

    def __str__(self):
        return f'{self.name}'


class Member(models.Model):
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
    phone_verified = models.BooleanField(default=False)
    email = models.EmailField(null=True, unique=True, blank=True)
    email_verified = models.BooleanField(default=False)
    address1 = models.CharField(max_length=256, blank=True, null=True)
    address2 = models.CharField(max_length=256, blank=True, null=True)
    country = models.CharField(max_length=128, blank=True, null=True)
    city = models.CharField(max_length=128, blank=True, null=True)
    state = models.CharField(max_length=128, blank=True, null=True)
    zipcode = models.CharField(max_length=10, blank=True, null=True)
    social_media = models.JSONField(null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, related_name='member', null=True)

    @property
    def is_verified(self):
        return self.email_verified or self.phone_verified

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
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
