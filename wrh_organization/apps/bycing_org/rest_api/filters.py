from django.db.models import Q
from django_filters import rest_framework as filters

from wrh_organization.helpers.utils import CharArrayFilter
from ..models import Member, Organization, OrganizationMember, OrganizationMemberOrg, FieldsTracking, Race, RaceResult, \
    Category, RaceSeries, RaceSeriesResult, Event


class MemberFilter(filters.FilterSet):
    class Meta:
        model = Member
        exclude = ['social_media', 'more_data']


class OrganizationFilter(filters.FilterSet):
    my = filters.BooleanFilter(method='my_method')
    managed_by_me = filters.BooleanFilter(method='managed_by_me_method')

    def my_method(self, queryset, name, value):
        user = self.request and self.request.user
        member = user and getattr(user, 'member', None)
        if value:
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
        exclude = ['social_media', 'logo', 'signup_config', 'membership_plans', 'member_fields_schema', 'members',
                   'member_orgs']


class OrganizationMemberFilter(filters.FilterSet):
    class Meta:
        model = OrganizationMember
        exclude = ['member_fields', 'membership_plan']


class OrganizationMemberOrgFilter(filters.FilterSet):
    class Meta:
        model = OrganizationMemberOrg
        exclude = ['member_fields']


class RaceFilter(filters.FilterSet):
    event = filters.ModelMultipleChoiceFilter(queryset=Event.objects.all())

    event_start_date__gte = filters.DateFilter(field_name='event__start_date', lookup_expr='gte')
    event_start_date__lte = filters.DateFilter(field_name='event__start_date', lookup_expr='lte')

    class Meta:
        model = Race
        exclude = ['more_data']


class RaceResultFilter(filters.FilterSet):
    event = filters.ModelMultipleChoiceFilter(queryset=Event.objects.all(), field_name='race__event')
    my = filters.BooleanFilter(method='my_method')

    def my_method(self, queryset, name, value):
        user = self.request and self.request.user
        member = user and getattr(user, 'member', None)
        if value:
            queryset = queryset.filter(rider=member) if (user and user.is_authenticated and member) else queryset.none()
        return queryset

    class Meta:
        model = RaceResult
        exclude = ['more_data']


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


class CategoryFilter(filters.FilterSet):
    class Meta:
        model = Category
        fields = '__all__'


class RaceSeriesFilter(filters.FilterSet):
    class Meta:
        model = RaceSeries
        exclude = ['points_map']


class RaceSeriesResultFilter(filters.FilterSet):
    my = filters.BooleanFilter(method='my_method')
    race = filters.ModelMultipleChoiceFilter(queryset=Race.objects.all(), field_name='race_result__race', label='Race')


    def my_method(self, queryset, name, value):
        user = self.request and self.request.user
        member = user and getattr(user, 'member', None)
        if value:
            queryset = queryset.filter(race_result__rider=member) if (user and user.is_authenticated and member) \
                else queryset.none()
        return queryset

    class Meta:
        model = RaceSeriesResult
        exclude = ['more_data']


class EventFilter(filters.FilterSet):
    id__in = filters.BaseInFilter(field_name='id')
    start_date__gte = filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date__lte = filters.DateFilter(field_name='start_date', lookup_expr='lte')
    end_date__gte = filters.DateFilter(field_name='end_date', lookup_expr='gte')
    end_date__lte = filters.DateFilter(field_name='end_date', lookup_expr='lte')
    tags = CharArrayFilter(field_name='tags', lookup_expr='contains', label='Tags')
    general = filters.BooleanFilter(field_name='organization', lookup_expr='isnull', label='Is General')

    class Meta:
        model = Event
        exclude = ['more_data', 'logo']


