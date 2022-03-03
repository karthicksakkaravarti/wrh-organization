# Generated by Django 4.0.1 on 2022-03-01 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bycing_org', '0009_alter_organizationmember_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='member',
            name='email_verified',
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='member',
            name='phone_verified',
            field=models.BooleanField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='organizationmember',
            name='org_member_uid',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='member',
            unique_together={('phone', 'phone_verified'), ('email', 'email_verified')},
        ),
    ]
