from dynamic_preferences.preferences import Section
from dynamic_preferences import types
from dynamic_preferences.registries import global_preferences_registry

from wrh_organization.helpers.utils import PatchedGlobalPrefFileSerializer

site_ui = Section('site_ui')
rollbar_client = Section('rollbar_client')
user_account = Section('user_account')
core_backend = Section('core_backend')

types.FilePreference.serializer_class = PatchedGlobalPrefFileSerializer


@global_preferences_registry.register
class UserAccountDisabledSignup(types.BooleanPreference):
    field_kwargs = {
        'required': False,
        'help_text': 'user account disabled signup',
    }
    section = user_account
    name = 'disabled_signup'
    verbose_name = 'Disabled Signup?'
    default = False


@global_preferences_registry.register
class CoreBackendDefaultOrgId(types.IntegerPreference):
    field_kwargs = {
        'required': False,
        'help_text': 'default organization id',
    }
    section = core_backend
    name = 'default_org_id'
    verbose_name = 'Default Org id'
    default = 1


@global_preferences_registry.register
class RollbarClientAccessToken(types.StringPreference):
    field_kwargs = {
        'required': False,
        'help_text': 'rollbar post client token',
    }
    section = rollbar_client
    name = 'access_token'
    verbose_name = 'Client Access Token'
    default = ''


@global_preferences_registry.register
class RollbarClientEnvironment(types.ChoicePreference):
    choices = [
        ('production', 'Production'),
        ('development', 'Development'),
    ]
    field_kwargs = {
        'required': False,
        'help_text': 'rollbar client environment',
    }
    section = rollbar_client
    name = 'environment'
    verbose_name = 'Client Environment'
    default = 'development'


@global_preferences_registry.register
class SiteUiTermsOfService(types.LongStringPreference):
    field_kwargs = {
        'required': False,
        'help_text': 'terms of service content',
    }
    section = site_ui
    name = 'terms_of_service'
    verbose_name = 'Terms of Service'
    default = ''


@global_preferences_registry.register
class SiteUiBannerImage(types.FilePreference):
    field_kwargs = {
        'required': False,
        'help_text': 'banner image of home site',
    }
    section = site_ui
    name = 'banner_image'
    verbose_name = 'Banner Image'


@global_preferences_registry.register
class SiteUiDefaultEventBannerImage(types.FilePreference):
    field_kwargs = {
        'required': False,
        'help_text': 'default banner image of event page',
    }
    section = site_ui
    name = 'default_event_banner_image'
    verbose_name = 'Default Event Banner Image'
