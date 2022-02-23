from django_filters import rest_framework as filters

from ..models import Member, Organization, OrganizationMember


class MemberFilter(filters.FilterSet):
    class Meta:
        model = Member
        fields = '__all__'


class OrganizationFilter(filters.FilterSet):
    my = filters.BooleanFilter(method='my_method')

    def my_method(self, queryset, name, value):
        user = self.request and self.request.user
        member = user and getattr(user, 'member', None)
        if value and user and user.is_authenticated and member:
            queryset = queryset.filter(members=member, organizationmember__is_valid=True).distinct()

        return queryset

    class Meta:
        model = Organization
        exclude = ['social_media', 'logo', 'signup_config', 'member_fields_schema']


class OrganizationMemberFilter(filters.FilterSet):
    class Meta:
        model = OrganizationMember
        exclude = ['member_fields']
