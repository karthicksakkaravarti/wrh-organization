# Generated by Django 4.0.6 on 2022-09-24 17:32

import apps.bycing_org.models
import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bycing_org', '0032_event_create_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to=apps.bycing_org.models.event_logo_file_path_func),
        ),
        migrations.AddField(
            model_name='event',
            name='registration_website',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='tags',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=100), blank=True, null=True, size=50),
        ),
        migrations.AddField(
            model_name='event',
            name='website',
            field=models.URLField(blank=True, null=True),
        ),
    ]