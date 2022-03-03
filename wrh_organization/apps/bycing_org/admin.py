from django.contrib import admin
from . import models


class OrganizationMemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'member', 'organization', 'status', 'is_active', 'datetime')
    list_filter = ('member', 'organization', 'status', 'is_active')


admin.site.register(models.Member)
admin.site.register(models.Organization)
admin.site.register(models.OrganizationMember, OrganizationMemberAdmin)
admin.site.register(models.OrganizationMemberOrg)
