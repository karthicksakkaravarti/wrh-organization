from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone
from model_utils import FieldTracker

User = get_user_model()


class ExtendedJSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        try:
            return super().default(o)
        except Exception as e:
            return str(o)


class BaseFieldsTracking(models.Model):
    _registry = {}

    object_id = models.CharField(max_length=64)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object = GenericForeignKey(ct_field='content_type', fk_field='object_id')
    fields_data = models.JSONField(null=True, blank=True, encoder=ExtendedJSONEncoder)
    changed_data = models.JSONField(null=True, blank=True, encoder=ExtendedJSONEncoder)
    object_repr = models.TextField()
    refs_repr = models.JSONField(null=True, blank=True, encoder=ExtendedJSONEncoder)
    datetime = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    user_str_id = models.CharField(max_length=64, null=True, blank=False)

    class Meta:
        abstract = True

    @property
    def _model(self):
        return self.content_type.model_class()

    @staticmethod
    def reg_key(model):
        return (model._meta.app_label, model._meta.model_name)

    @classmethod
    def reg_opts(cls, model):
        return cls._registry[cls.reg_key(model)]

    @classmethod
    def get_query_for_models(cls, *models):
        content_types = ContentType.objects.get_for_models(*models)
        return cls.objects.filter(content_type__in=[c.id for c in content_types.values()])

    @classmethod
    def get_field_history_user(cls, instance, **opts):
        from wrh_organization.helpers.middleware import get_current_user

        if opts.get('user_field'):
            return getattr(instance, opts['user_field'])
        user = get_current_user()
        if user and user.is_authenticated:
            return user

    @classmethod
    def track(cls, sender, instance, **kwargs):
        model = sender
        content_type = ContentType.objects.get_for_model(model)
        opts = cls.reg_opts(model)
        user = cls.get_field_history_user(instance, **opts)
        tracker = getattr(instance, opts['tracker_field'])
        prev_changed = tracker.changed()
        current_data = tracker.current()
        changed_data = {f: current_data[f] for f in prev_changed}
        refs_repr = {}
        for f, v in prev_changed.items():
            field = model._meta.get_field(f)
            if isinstance(field, models.ForeignKey):
                prev = field.related_model.objects.filter(pk=v).first()
                current = getattr(instance, f, None)
                refs_repr[f] = {'p': prev and str(prev), 'c': current and str(current)}  # p = previous, c = current

        created = kwargs.get('created')
        fields_data = None if created else tracker.saved_data
        dt = getattr(instance, '_override_tracker_datetime', None) or timezone.now()
        if changed_data:
            cls.objects.create(object_id=str(instance.pk), object_repr=str(instance), content_type=content_type,
                               user=user, fields_data=fields_data, changed_data=changed_data, refs_repr=refs_repr,
                               user_str_id=user and str(user.pk), datetime=dt)

    @classmethod
    def register(cls, model=None, tracker_field='_tracker', user_field=None):
        def wrapper(model):
            reg_key = cls.reg_key(model)
            assert reg_key not in cls._registry, '{} has already been registered in BaseFieldsTracking'.format(model)
            tracker = getattr(model, tracker_field, None)
            assert bool(tracker) and isinstance(tracker, FieldTracker), \
                'you should set a "{}" field in "{}" class'.format(tracker_field, model)

            cls._registry[reg_key] = dict(tracker_field=tracker_field, user_field=user_field)
            post_save.connect(cls.track, sender=model)
            return model

        if model is None:
            return wrapper
        return wrapper(model)

    def __str__(self):
        return self.object_repr
