from django.db.models import Q
from django_filters import rest_framework as filters

from ..models import Member, Organization, OrganizationMember


class MemberFilter(filters.FilterSet):
    class Meta:
        model = Member
        exclude = ['social_media']


class OrganizationFilter(filters.FilterSet):
    my = filters.BooleanFilter(method='my_method')
    my_adminated = filters.BooleanFilter(method='my_adminated_method')

    def my_method(self, queryset, name, value):
        user = self.request and self.request.user
        member = user and getattr(user, 'member', None)
        if value and user and user.is_authenticated and member:
            queryset = queryset.filter(members=member, organizationmember__is_active=True).distinct()

        return queryset

    def my_adminated_method(self, queryset, name, value):
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
