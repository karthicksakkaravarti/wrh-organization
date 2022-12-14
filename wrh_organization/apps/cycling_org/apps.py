import stripe
from django.apps import AppConfig
from django.conf import settings


class CyclingOrgConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.cycling_org'
    verbose_name = 'Cycling Org'

    def ready(self):
        # configure stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.proxy = getattr(settings, 'STRIPE_PROXY', None)
