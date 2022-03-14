from django.contrib import admin
from . import models


class OrganizationMemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'member', 'organization', 'status', 'is_active', 'datetime')
    list_filter = ('member', 'organization', 'status', 'is_active')


class OrganizationMemberOrgAdmin(admin.ModelAdmin):
    list_display = ('id', 'member_org', 'organization', 'status', 'is_active', 'datetime')
    list_filter = ('member_org', 'organization', 'status', 'is_active')


class MemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'phone', 'user')
    search_fields = ('first_name', 'last_name')
    list_filter = ('email_verified', 'phone_verified')


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'website',)
    search_fields = ('name', 'website', 'email', 'phone')
    list_filter = ('type',)


class FieldsTrackingAdmin(admin.ModelAdmin):
    list_display = ('id', 'object_id', 'content_type', 'object_repr', 'datetime', 'user')
    search_fields = ('object_repr',)
    list_filter = ('content_type',)


admin.site.register(models.Member, MemberAdmin)
admin.site.register(models.Organization, OrganizationAdmin)
admin.site.register(models.OrganizationMember, OrganizationMemberAdmin)
admin.site.register(models.OrganizationMemberOrg, OrganizationMemberOrgAdmin)
admin.site.register(models.FieldsTracking, FieldsTrackingAdmin)
