from __future__ import absolute_import
import logging
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from huey.contrib.djhuey import db_periodic_task
from apps.bycing_org.models import OrganizationMember

logger = logging.getLogger('huey')


@db_periodic_task(settings.HUEY_TASKS_PERIODS['bycing_org_disable_expired_memberships'])
def disable_expired_memberships():
    logger.info('Disabling expired membership...')
    today = timezone.now().date()
    qs = OrganizationMember.objects.exclude(
        Q(exp_date__isnull=True) | Q(is_master_admin=True) | Q(is_admin=True)
    ).filter(is_active=True, exp_date__lt=today)
    res = qs.update(is_active=False)
    logger.info('Disabled expired membership: %s', res)
