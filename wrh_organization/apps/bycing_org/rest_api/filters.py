from django_filters import rest_framework as filters

from apps.bycing_org.models import Member, Organization


class MemberFilter(filters.FilterSet):
    class Meta:
        model = Member
        fields = '__all__'


class OrganizationFilter(filters.FilterSet):
    class Meta:
        model = Organization
        exclude = ['social_media', 'logo', 'signup_config']
