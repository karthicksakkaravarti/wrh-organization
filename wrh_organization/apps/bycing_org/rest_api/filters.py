from django.db.models import Q
from django_filters import rest_framework as filters

from ..models import Member, Organization, OrganizationMember, OrganizationMemberOrg, FieldsTracking


class MemberFilter(filters.FilterSet):
    class Meta:
        model = Member
        exclude = ['social_media']


class OrganizationFilter(filters.FilterSet):
    my = filters.BooleanFilter(method='my_method')
    managed_by_me = filters.BooleanFilter(method='managed_by_me_method')

    def my_method(self, queryset, name, value):
        user = self.request and self.request.user
        member = user and getattr(user, 'member', None)
        if value and user and user.is_authenticated and member:
            ids = OrganizationMember.objects.filter(is_active=True, member=member).exclude(
                status__in=(OrganizationMember.STATUS_REJECT, OrganizationMember.STATUS_WAITING)
            ).values_list('organization', flat=True)
            queryset = queryset.filter(id__in=list(ids))

        return queryset

    def managed_by_me_method(self, queryset, name, value):
        user = self.request and self.request.user
        member = user and getattr(user, 'member', None)
        if value and user and user.is_authenticated and member:
            ids = OrganizationMember.objects.filter(is_active=True, member=member).filter(
                Q(is_admin=True) | Q(is_master_admin=True)).values_list('organization', flat=True)
            queryset = queryset.filter(id__in=list(ids))

        return queryset

    class Meta:
        model = Organization
        exclude = ['social_media', 'logo', 'signup_config', 'member_fields_schema', 'members', 'member_orgs']


class OrganizationMemberFilter(filters.FilterSet):
    class Meta:
        model = OrganizationMember
        exclude = ['member_fields']


class OrganizationMemberOrgFilter(filters.FilterSet):
    class Meta:
        model = OrganizationMemberOrg
        exclude = ['member_fields']


class FieldsTrackingFilter(filters.FilterSet):
    min_id = filters.NumberFilter(field_name='id', lookup_expr='gt')
    date = filters.DateFilter(field_name='datetime__date', label='Date')
    min_datetime = filters.IsoDateTimeFilter(field_name='datetime', lookup_expr='gte')
    max_datetime = filters.IsoDateTimeFilter(field_name='datetime', lookup_expr='lt')
    changed_data_keys = filters.BaseCSVFilter(field_name='changed_data', lookup_expr='has_any_keys')
    model_name = filters.CharFilter(field_name='content_type__model', label='Model Name')

    class Meta:
        model = FieldsTracking
        fields = ['min_datetime', 'max_datetime', 'date', 'min_id', 'object_id', 'changed_data_keys', 'user_str_id',
                  'user', 'content_type']



