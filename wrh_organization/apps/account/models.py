import os

from django.contrib.auth.models import AbstractUser
from django.db import models


def avatar_file_path_func(instance, filename):
    from wrh_organization.helpers.utils import get_random_upload_path
    return get_random_upload_path(os.path.join('uploads', 'user', 'avatar'), filename)


class User(AbstractUser):
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

    email = models.EmailField(unique=True, blank=False)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default=GENDER_UNKNOWN)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(blank=True, null=True, upload_to=avatar_file_path_func)
    # verified_email = models.BooleanField(default=False)
