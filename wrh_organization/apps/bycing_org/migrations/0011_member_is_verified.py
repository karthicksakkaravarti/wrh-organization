# Generated by Django 4.0.1 on 2022-03-01 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bycing_org', '0010_alter_member_email_alter_member_email_verified_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='is_verified',
            field=models.BooleanField(default=None, null=True),
        ),
    ]
