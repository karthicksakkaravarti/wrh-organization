from dynamic_preferences.preferences import Section
from dynamic_preferences import types
from dynamic_preferences.registries import global_preferences_registry

site_ui = Section('site_ui')


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
