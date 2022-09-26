import django_filters
from apps.usacycling import models

from wrh_organization.helpers.utils import CharArrayFilter


class USACyclingClubFilter(django_filters.FilterSet):
    club_aff_type__aff_type_description = django_filters.CharFilter(
        method='aff_type_description_filter'
    )

    def aff_type_description_filter(self, queryset, name, value):
        return queryset.filter(club_aff_type__aff_type_description__iexact=value)

    class Meta:
        model = models.USACClub
        fields = ['club_aff_type__aff_type_description']


class USACEventFilter(django_filters.FilterSet):
    event_id__in = django_filters.BaseInFilter(field_name='event_id')
    start_date = django_filters.CharFilter(lookup_expr='iexact')
    start_date__gte = django_filters.CharFilter(field_name='start_date', lookup_expr='gte')
    start_date__lte = django_filters.CharFilter(field_name='start_date', lookup_expr='lte')
    end_date__gte = django_filters.CharFilter(field_name='end_date', lookup_expr='gte')
    end_date__lte = django_filters.CharFilter(field_name='end_date', lookup_expr='lte')
    labels = CharArrayFilter(field_name='labels', lookup_expr='contains')

    class Meta:
        model = models.USACEvent
        fields = ['start_date', 'start_date__gte', 'start_date__lte', 'end_date__gte', 'end_date__lte',
                  'labels', 'is_featured', 'is_usac_sanctioned']
