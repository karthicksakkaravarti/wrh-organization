from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField

User = get_user_model()


class OrganizationMember(models.Model):
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE)
    member = models.ForeignKey('Member', on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    membership_price = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    datetime = models.DateTimeField(auto_now_add=True)


class OrganizationMemberOrg(models.Model):
    organization = models.ForeignKey('Organization', related_name='organizaton_member_orgs', on_delete=models.CASCADE)
    top_organization = models.ForeignKey('Organization', related_name='top_organizaton_member_orgs', on_delete=models.CASCADE)
    membership_price = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    datetime = models.DateTimeField(auto_now_add=True)


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
    about = models.TextField(null=True, blank=True)
    logo = models.ImageField(null=True, blank=True)
    signup_config = models.JSONField(null=True)
    members = models.ManyToManyField('Member', related_name='organizations', through=OrganizationMember)
    member_orgs = models.ManyToManyField('Organization', related_name='organizations', through=OrganizationMemberOrg)


class Member(models.Model):
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
    phone = PhoneNumberField(max_length=50, unique=True, null=True, blank=True)
    phone_verified = models.BooleanField(default=False)
    email = models.EmailField(null=True, unique=True, blank=True)
    email_verified = models.BooleanField(default=False)
    address1 = models.CharField(max_length=256, blank=True, null=True)
    address2 = models.CharField(max_length=256, blank=True, null=True)
    country = models.CharField(max_length=128, blank=True, null=True)
    city = models.CharField(max_length=128, blank=True, null=True)
    state = models.CharField(max_length=128, blank=True, null=True)
    zipcode = models.CharField(max_length=10, blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, related_name='member', null=True)


# @receiver(post_save, sender=User)
# def new_user_created(sender, instance, **kwargs):
#     if kwargs.get('created') and not instance.is_superuser:
#         Member.objects.update_or_create(
#             defaults=dict(
#                 first_name=instance.first_name, last_name=instance.last_name, gender=instance.gender,
#                 birth_date=instance.birth_date, user=instance
#             ),
#             email=instance.email
#         )
