import traceback

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db import transaction

from .models import User
from ..cycling_org.models import Member
from ..cycling_org.rest_api.views import _send_activation_email


@admin.action(description='Activate rider member account')
def activate_member(modeladmin, request, queryset):
    for user in queryset:
        member = getattr(user, 'member', None)
        if member and member.email_verified:
            continue
        try:
            with transaction.atomic():
                existing_member = Member.objects.exclude(user=user).filter(email=user.email
                                                                           ).order_by('email_verified').first()
                member = existing_member or member

                member = Member() if member is None else member

                member.set_as_verified(user)
                user.is_active = True
                user.save()
        except Exception:
            traceback.print_exc()


@admin.action(description='Send E-mail activation link')
def send_activation_link(modeladmin, request, queryset):
    for user in queryset.exclude(is_active=True):
        _send_activation_email(user, request)


class UserAdmin(BaseUserAdmin):
    list_display = ['id', 'username', 'first_name', 'last_name', 'gender', 'is_active',
                    'has_rider_member_account', 'date_joined', 'draft']
    actions = [activate_member, send_activation_link]

    @admin.display(boolean=True)
    def has_rider_member_account(self, obj):
        return True if getattr(obj, 'member', None) else False

    has_rider_member_account.short_description = 'Rider Member?'


admin.site.register(User, UserAdmin)
