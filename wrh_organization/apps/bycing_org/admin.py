from django.contrib import admin
from . import models


admin.site.register(models.Member)
admin.site.register(models.Organization)
admin.site.register(models.OrganizationMember)
admin.site.register(models.OrganizationMemberOrg)
