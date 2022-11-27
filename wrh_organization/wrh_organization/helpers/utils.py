import base64
import datetime
import decimal
import functools
import os
import random
import re
import string
import traceback
import uuid
from functools import wraps

import json

import cerberus
import pyotp
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import PermissionRequiredMixin as DjangoPermissionRequiredMixin
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied, ValidationError, RequestDataTooBig
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile
from django.core.mail.backends.filebased import EmailBackend
from django.db import IntegrityError, models
from django.db.models import ProtectedError, Q
from django.http import Http404, QueryDict, HttpResponseForbidden
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime, parse_date
from django.utils.encoding import iri_to_uri
from django.utils.safestring import mark_safe
from django.utils.timezone import is_aware, make_aware
from django.utils.translation import gettext_lazy as _
from django_filters import OrderingFilter
from django_filters.filters import EMPTY_VALUES
from django_filters import filters
from phonenumber_field.phonenumber import PhoneNumber
from rest_framework import status, parsers, serializers, permissions
from rest_framework.exceptions import APIException
from rest_framework.filters import OrderingFilter as OrderingFilterBackend
from rest_framework.pagination import PageNumberPagination, _positive_int
from rest_framework.permissions import DjangoModelPermissions, BasePermission
from rest_framework.response import Response
from sendsms import api
from sendsms.backends.base import BaseSmsBackend
from storages.backends.s3boto3 import S3Boto3Storage, SpooledTemporaryFile
from twilio.request_validator import RequestValidator
from twilio.rest import Client as TwilioRestClient

print = functools.partial(print, flush=True)

time_type = cerberus.TypeDefinition('time', (datetime.time,), ())
cerberus.Validator.types_mapping['time'] = time_type
decimal_type = cerberus.TypeDefinition('decimal', (decimal.Decimal,), ())
cerberus.Validator.types_mapping['decimal'] = decimal_type

User = get_user_model()


class CustomFileBasedEmailBackend(EmailBackend):
    def write_message(self, message):
        res = super(CustomFileBasedEmailBackend, self).write_message(message)
        if getattr(settings, 'EMAIL_BODY_TO_FILE'):
            try:
                with open(settings.EMAIL_BODY_TO_FILE, 'w') as f:
                    f.write(str(message.body))
            except Exception:
                traceback.print_exc()
        if getattr(settings, 'EMAIL_BODY_TO_CONSOLE') is True:
            print(message.body)
        return res


class NotFoundView(object):
    @classmethod
    def as_view(cls):
        return cls.handler

    @classmethod
    def handler(cls, request):
        raise Http404


class BulkableActionMixin(object):
    pk_url_kwarg = 'pk'

    def get_bulk_ids(self):
        return [int(i) for i in self.kwargs.get(self.pk_url_kwarg).rstrip(',').split(',')]

    def get_queryset(self):
        ids = self.get_bulk_ids()
        qs = self.model.objects
        return get_object_or_404(qs, id=ids[0]) if len(ids) == 1 else qs.filter(id__in=ids)


# noinspection PyClassHasNoInit
class PermissionRequiredMixin(DjangoPermissionRequiredMixin):
    def get_permission_required(self):
        perms = self.permission_required or ()
        if isinstance(perms, dict):
            perms = perms.get(self.request.method.lower(), ()) or ()

        if isinstance(perms, str):
            perms = (perms,)

        return perms

    def handle_no_authenticated(self):
        if self.request.is_ajax():
            return JsonResponse({'error': 'Not Authorized'}, status=401)
        return redirect_to_login(self.request.get_full_path(),
                                 self.get_login_url(),
                                 self.get_redirect_field_name())

    def handle_no_permission(self):
        if self.request.is_ajax():
            return JsonResponse({'error': 'Permission Denied'}, status=403)
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        return render(self.request, "no-permission.html", status=403)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_authenticated()
        if not self.has_permission():
            return self.handle_no_permission()
        return super(PermissionRequiredMixin, self
                     ).dispatch(request, *args, **kwargs)


class NotSet:
    pass


def to_dict(obj, fields=None, fields_map=None, extra_fields=None, exclude_fields=None, default_convert=True):
    """
    convert a model object to a python dict.
    @param obj: database model object
    @param fields: list of fields which we want to show in return value.
        if fields=None, we show all fields of model object
    @type fields: list
    @param fields_map: a map converter to show fields as a favorite.
        every field can bind to a lambda function in fields_map.
        if a field was bind to a None value in fields_map, we ignore this field
        to show in result
    @type fields_map: dict
    @param extra_fields: extra fields to be listed in result
    @param default_convert: convert fields as default.
    """
    from django.db import models
    data = {}
    fields_map = fields_map or {}
    exclude_fields = exclude_fields or []

    if fields is None:
        # noinspection PyProtectedMember
        fields = [f.name for f in obj.__class__._meta.fields]

    fields.extend(extra_fields or [])
    fields = [f for f in fields if f not in exclude_fields]
    for field in fields:
        if field in fields_map:
            if fields_map[field] is None:
                continue
            v = fields_map.get(field)()
        else:
            v = getattr(obj, field, None)
        if default_convert:
            if isinstance(v, datetime.datetime):
                data[field] = v.isoformat() + 'Z'
            elif isinstance(v, datetime.date):
                data[field] = v.isoformat()
            elif isinstance(v, decimal.Decimal):
                # noinspection PyTypeChecker
                data[field] = float(v)
            elif isinstance(v, models.Model):
                data[field] = v.id
            else:
                data[field] = v
        else:
            data[field] = v

    return data


def random_id(n=8, no_upper=False, no_lower=False, no_digit=False):
    rand = random.SystemRandom()
    chars = ''
    if no_upper is False:
        chars += string.ascii_uppercase
    if no_lower is False:
        chars += string.ascii_lowercase
    if no_digit is False:
        chars += string.digits
    if not chars:
        raise Exception('chars is empty! change function args!')
    return ''.join([rand.choice(chars) for _ in range(n)])


def end_of_month(date):
    return (date.replace(day=15) + datetime.timedelta(days=20)).replace(day=1) - datetime.timedelta(days=1)


def success_message(message, request):
    return messages.success(request, mark_safe(message))


def error_message(message, request):
    return messages.error(request, mark_safe(message), extra_tags='danger')


def info_message(message, request):
    return messages.info(request, mark_safe(message))


def warning_message(message, request):
    return messages.warning(request, mark_safe(message))


def send_form_errors(form, request):
    msgs = []
    for k, v in form.errors.items():
        msg = '' if k.startswith('__') else '{0}: '.format(k)
        msgs.append('<li>{0}{1}</li>'.format(msg, ', '.join(v)))

    if msgs:
        return error_message(''.join(msgs), request)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def send_sms(message, to, from_=None, fail_silently=False):
    from_ = from_ or settings.SMS_DEFAULT_FROM_PHONE
    if isinstance(to, str):
        to = [to]
    return api.send_sms(body=message, from_phone=from_, to=to, fail_silently=fail_silently)


# noinspection PyProtectedMember
def fetch_tracking_info(request):
    ua = request.user_agent
    return dict(
        os=dict(ua.os._asdict()) if ua.os else {},
        device=dict(ua.device._asdict()) if ua.device else {},
        browser=dict(ua.browser._asdict()) if ua.browser else {},
        is_bot=ua.is_bot,
        is_mobile=ua.is_mobile,
        is_pc=ua.is_pc,
        is_tablet=ua.is_tablet,
        is_touch_capable=ua.is_touch_capable,
        ip_address=get_client_ip(request)
    )


def get_aware_datetime(date_str):
    ret = parse_datetime(date_str)
    if not is_aware(ret):
        ret = make_aware(ret)
    return ret


def get_current_page_size(request, default=None):
    page_size = default or settings.PAGINATION_DEFAULT_PAGINATION
    try:
        page_size = int(request.GET.get('page_size'))
    except (ValueError, TypeError):
        pass

    if page_size <= 0:
        page_size = default or settings.PAGINATION_DEFAULT_PAGINATION
    return min(page_size, settings.PAGINATION_MAX_SIZE)


def get_file_type_by_extension(file_name):
    _, ext = os.path.splitext(file_name)
    if not ext:
        return None
    ext = ext.lstrip('.').lower()
    formats = {
        'image': ('jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg',),
        'video': ('avi', 'mov', 'flv', 'mp4', 'mpg', 'mpeg', 'wmv', '3gp',),
        'audio': ('mp3', '3gp', 'amr', 'ogg', 'wma', 'wav',),
        'pdf': ('pdf',),
        'word': ('doc', 'docx', 'odt',),
        'excel': ('xls', 'xlsx', 'ods',),
        'powerpoint': ('ppt', 'pptx', 'odp',),
    }

    for fmt, exts in formats.items():
        if ext in exts:
            return fmt


def get_random_upload_path(upload_dir, filename):
    ext = filename.split('.')[-1]
    randid = random_id(n=8)
    filename = "{0}-{1}.{2}".format(uuid.uuid4(), randid, ext)
    return os.path.join(upload_dir, filename)


class ExtendedOrderingFilter(OrderingFilter):
    def __init__(self, *args, **kwargs):
        self.ordering_map = kwargs.pop('ordering_map', {})
        super(ExtendedOrderingFilter, self).__init__(*args, **kwargs)

    def get_ordering_value(self, param):
        descending = param.startswith('-')
        param = param[1:] if descending else param
        field_name = self.param_map.get(param, param)
        field_name = self.ordering_map.get(field_name, field_name)
        if callable(field_name):
            res = field_name(descending)
            if not isinstance(res, (tuple, list)):
                res = [res]
            return res
        if isinstance(field_name, str):
            field_name = (field_name,)

        return [("-%s" % f if descending else f) for f in field_name]

    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs

        ordering = []
        for param in value:
            ordering.extend(list(self.get_ordering_value(param)))
        return qs.order_by(*ordering)


class SmsBackend(BaseSmsBackend):
    def send_messages(self, msgs):
        client = TwilioRestClient(settings.SENDSMS_TWILIO_ACCOUNT_SID, settings.SENDSMS_TWILIO_AUTH_TOKEN)
        results = []
        for msg in msgs:
            to_res = []
            for to in msg.to:
                try:
                    message = client.messages.create(
                        to=to,
                        from_=msg.from_phone or settings.SMS_DEFAULT_FROM_PHONE,
                        body=msg.body
                    )
                    to_res.append(message)
                except Exception:
                    if not self.fail_silently:
                        raise
                    to_res.append(None)
            results.append(to_res)
        if len(results) == 1:
            results = results[0]
            if len(results) == 1:
                results = results[0]
        return results


def to_query_dict(d):
    qdict = QueryDict('', mutable=True)
    for key, value in d.items():
        if not isinstance(value, list):
            value = [value]
        qdict.setlist(key, value)
    return qdict


def validate_twilio_request(f):
    """Validates that incoming requests genuinely originated from Twilio"""

    @wraps(f)
    def decorated_function(request, *args, **kwargs):
        # Create an instance of the RequestValidator class
        validator = RequestValidator(settings.SENDSMS_TWILIO_AUTH_TOKEN)

        # Validate the request using its URL, POST data,
        # and X-TWILIO-SIGNATURE header
        path = request.META.get('HTTP_ORIGIN_PATH_INFO') or request.path
        scheme = request.META.get('HTTP_ORIGIN_SCHEME') or request.scheme
        qs = request.META.get('QUERY_STRING', '')
        qs = ('?' + iri_to_uri(qs)) if qs else ''
        uri = '{scheme}://{host}{path}{qs}'.format(scheme=scheme, host=request.get_host(), path=path, qs=qs)
        params = request.POST if request.method == 'POST' else request.GET
        signature = request.META.get('HTTP_X_TWILIO_SIGNATURE', '')
        request_valid = validator.validate(uri, params, signature)

        # Continue processing the request if it's valid, return a 403 error if
        # it's not
        if request_valid or settings.TWILIO_DEBUG:
            return f(request, *args, **kwargs)
        else:
            print("!!! Skipped spam request !!!")
            print(uri, params, signature)
            print(request.META)
            return HttpResponseForbidden()

    return decorated_function


def humanify_phone(phone):
    if isinstance(phone, str):
        phone = PhoneNumber.from_string(phone, settings.PHONENUMBER_DEFAULT_REGION)
    p = phone.as_international.split(' ', 1)
    return p[1] if len(p) == 2 else p[0]


def international_phone(phone):
    if isinstance(phone, str):
        phone = PhoneNumber.from_string(phone, settings.PHONENUMBER_DEFAULT_REGION)
    return str(phone)


class S3MediaStorage(S3Boto3Storage):
    location = getattr(settings, 'AWS_MEDIA_LOCATION', 'media')


class S3PublicMediaStorage(S3Boto3Storage):
    location = getattr(settings, 'AWS_MEDIA_LOCATION', 'media')
    querystring_auth = False
    bucket_name = settings.AWS_PUBLIC_STORAGE_BUCKET_NAME
    default_acl = 'public-read'
    bucket_acl = default_acl
    custom_domain = getattr(settings, 'AWS_S3_MEDIA_CUSTOM_DOMAIN', None)


class S3StaticStorage(S3Boto3Storage):
    location = getattr(settings, 'AWS_STATIC_LOCATION', 'static')
    querystring_auth = False
    bucket_name = settings.AWS_PUBLIC_STORAGE_BUCKET_NAME
    default_acl = 'public-read'
    bucket_acl = default_acl
    custom_domain = getattr(settings, 'AWS_S3_STATIC_CUSTOM_DOMAIN', None)


class MultiUploadMetaInput(forms.ClearableFileInput):
    """ HTML5 <input> representation. """

    def __init__(self, *args, **kwargs):
        self.multiple = kwargs.pop('multiple', True)
        super(MultiUploadMetaInput, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        if self.multiple:
            attrs['multiple'] = 'multiple'

        return super(MultiUploadMetaInput, self).render(name, value, attrs, renderer)

    def value_from_datadict(self, data, files, name):
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        else:
            value = files.get(name)
            if isinstance(value, list):
                return value
            else:
                return [value]


class MultiFileField(forms.FileField):
    default_error_messages = {
        'min_num': _(
            'Ensure at least %(min_num)s files are '
            'uploaded (received %(num_files)s).'),
        'max_num': _(
            'Ensure at most %(max_num)s files '
            'are uploaded (received %(num_files)s).'),
        'file_size': _(
            'File %(uploaded_file_name)s '
            'exceeded maximum upload size.'),
    }

    def __init__(self, *args, **kwargs):
        self.min_num = kwargs.pop('min_num', 0)
        self.max_num = kwargs.pop('max_num', None)
        self.maximum_file_size = kwargs.pop('max_file_size', None)
        self.widget = MultiUploadMetaInput(
            attrs=kwargs.pop('attrs', {}),
            multiple=(self.max_num is None or self.max_num > 1),
        )
        super(MultiFileField, self).__init__(*args, **kwargs)

    def to_python(self, data):
        ret = []
        data = data or []
        for item in data:
            i = super(MultiFileField, self).to_python(item)
            if i:
                ret.append(i)
        return ret

    def validate(self, data):
        super(MultiFileField, self).validate(data)

        num_files = len(data)
        if num_files and not data[0]:
            num_files = 0

        if not self.required and num_files == 0:
            return

        if num_files < self.min_num:
            raise ValidationError(
                self.error_messages['min_num'] % {
                    'min_num': self.min_num,
                    'num_files': num_files,
                }
            )
        elif self.max_num and num_files > self.max_num:
            raise ValidationError(
                self.error_messages['max_num'] % {
                    'max_num': self.max_num,
                    'num_files': num_files,
                }
            )

        for uploaded_file in data:
            if (self.maximum_file_size and
                    uploaded_file.size > self.maximum_file_size):
                raise ValidationError(
                    self.error_messages['file_size'] % {
                        'uploaded_file_name': uploaded_file.name,
                    }
                )


def get_start_of_week(date=None, weeks_ago=0):
    date = date or timezone.now().date()
    return date - datetime.timedelta(days=weeks_ago * 7 + (date.isoweekday() % 7))


@functools.total_ordering
class MinType(object):
    def __le__(self, other):
        return True

    def __eq__(self, other):
        return (self is other)


class PySortableMixin(object):
    sort_fields = {}
    default_sort_field = None

    def pysort_records(self, records, sort_field, sort_fields=None):
        sort_fields = sort_fields or self.sort_fields
        if not sort_fields:
            return
        if isinstance(sort_fields, (list, tuple)):
            sort_fields = {k: None for k in sort_fields}
        default_sort_field = self.default_sort_field if self.default_sort_field in sort_fields \
            else list(sort_fields.keys())[0]
        is_reverse_sorting = sort_field.startswith('-')
        sort_field = sort_field.lstrip('-+')
        if sort_field not in sort_fields:
            sort_field = default_sort_field
            is_reverse_sorting = False
        min_type = MinType()

        def sort_key_func(r):
            import inspect
            value = r.get(sort_field)
            if sort_fields[sort_field] is not None:
                fn = sort_fields[sort_field]
                ins = inspect.getfullargspec(fn)
                if len(ins.args) == 1:
                    value = fn(value)
                elif len(ins.args) == 2:
                    value = fn(value, r)
            if isinstance(value, (list, tuple)):
                value = tuple((min_type if i is None else i) for i in value)
            return min_type if value is None else value

        records.sort(key=sort_key_func, reverse=is_reverse_sorting)


class DuplicateError(APIException):
    status_code = status.HTTP_409_CONFLICT


class ServiceUnavailable(APIException):
    status_code = 503
    default_detail = 'Service temporarily unavailable, try again later.'


class APICodeException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, status_code=status.HTTP_400_BAD_REQUEST, detail=None, code=None):
        self.status_code = status_code
        super().__init__(detail=detail, code=code)


def custom_rest_exception_handler(exc, context):
    """ Custom rest api exception handler """
    from rest_framework import exceptions
    from rest_framework.views import exception_handler, set_rollback
    response = exception_handler(exc, context)
    err_msg = str(exc)

    if isinstance(exc, RequestDataTooBig):
        return Response({'reason': 'too big data or file upload'}, status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

    if isinstance(exc, ProtectedError):
        data = {'reason': ' Not able to delete, there are links to this record and is protected.'}
        traceback.print_exc()
        set_rollback()
        return Response(data, status=status.HTTP_412_PRECONDITION_FAILED)

    if isinstance(exc, IntegrityError) and ('already exists' in err_msg or 'must make a unique set' in err_msg or
                                            'must be unique' in err_msg):
        data = {'reason': 'duplicate unique key'}
        set_rollback()
        return Response(data, status=status.HTTP_409_CONFLICT)

    if response is None:
        if isinstance(exc, ValidationError):
            return Response(exc.message_dict, status=status.HTTP_400_BAD_REQUEST)
        traceback.print_exc()
        return Response({'reason': 'unexpected server error'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR, exception=True)

    if isinstance(exc, exceptions.NotAuthenticated):
        response.status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, exceptions.ValidationError) and (
            'already exists' in err_msg or 'must make a unique set' in err_msg or 'must be unique' in err_msg):
        response.status_code = status.HTTP_409_CONFLICT

    return response


class DynamicFieldsSerializerMixin(object):
    """
    This class allow you to have dynamic fields in get rest api.
    user can pass "fields" and "xfields" as a get query parameter.
    "fields" specify list of fields you want to be shown as a result.
    "xfields" specify list of fields you want to be excluded in result.
    i.e:
    fields=id,name
    or
    xfields=name1,name2
    """
    extra_fields = []

    def __init__(self, *args, **kwargs):
        super(DynamicFieldsSerializerMixin, self).__init__(*args, **kwargs)
        if not self.context:
            return

        params = self.context['request'].query_params
        fields = params.get('fields')
        xfields = params.get('xfields')
        exfields = (params.get('exfields') or '').split(',')
        if fields:
            fields = fields.split(',')
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)
        if xfields:
            xfields = xfields.split(',')
            for field_name in xfields:
                self._exclude_field(field_name.split('.'))

        for extra_field in self.extra_fields:
            if extra_field not in exfields:
                self._exclude_field(extra_field.split('.'))

    def _exclude_field(self, field_name, fields_container=None):
        if fields_container == None:
            fields_container = self.fields

        if len(field_name) == 1:
            return fields_container.pop(field_name[0], None)
        inner_fields = fields_container.get(field_name[0], None)
        if not inner_fields:
            return
        return self._exclude_field(field_name[1:], inner_fields.fields)


class ExtendedOrderingFilterBackend(OrderingFilterBackend):
    def get_valid_fields(self, queryset, view, context=None):
        fields = super(ExtendedOrderingFilterBackend, self).get_valid_fields(queryset, view, context=context or {})
        extra_fields = getattr(view, 'extra_ordering_fields', {}) or {}
        fields.extend([(item, item) for item in extra_fields.keys()])
        return fields

    def get_ordering(self, request, queryset, view):
        fields = super(ExtendedOrderingFilterBackend, self).get_ordering(request, queryset, view)
        extra_fields = getattr(view, 'extra_ordering_fields', {}) or {}
        if not extra_fields:
            return fields
        new_fields = []
        for field in fields:
            descending = field.startswith('-')
            field = field[1:] if descending else field
            field_ordering = extra_fields.get(field, field)
            if callable(field_ordering):
                field_ordering = field_ordering(descending)
                if not isinstance(field_ordering, (list, tuple)):
                    field_ordering = (field_ordering,)
            else:
                if isinstance(field_ordering, str):
                    field_ordering = (field_ordering,)
                field_ordering = ['{}{}'.format('-' if descending else '', f) for f in field_ordering]
            new_fields.extend(field_ordering)
        return new_fields


class CustomDjangoModelPermissions(DjangoModelPermissions):
    perms_map = {
        'OPTIONS': [],
        'HEAD': [],
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }


class ExplicitPermissions(BasePermission):
    '''
    set this as a member of permission_classes field of view. i.e:
    permission_classes=(permissions.IsAuthenticated, ExplicitPermissions)

    in View classs we need to have a class property called 'explicit_permissions'. i.e:
    explicit_permissions = 'student.view_therapiststudentassigned'
    explicit_permissions = ['student.view_therapiststudentassigned', 'student.add_therapiststudentassigned']
    explicit_permissions = {
        'staff_assign': 'student.view_therapiststudentassigned'
    }
    explicit_permissions = {
        'staff_assign': {
            'get': 'student.view_therapiststudentassigned',
            'post': 'student.add_therapiststudentassigned'
        }
    }
    '''

    def has_permission(self, request, view):
        perms = getattr(view, 'explicit_permissions', None)
        http_method = request.method.lower()
        action = view.action
        if isinstance(perms, dict):
            perms = perms.get(action, []) or []
        if isinstance(perms, dict):
            perms = perms.get(http_method, []) or []
        if isinstance(perms, str):
            perms = [perms]
        return True if not perms else request.user.has_perms(perms)


class IsOwnerPermission(permissions.BasePermission):

    @staticmethod
    def __discover_owner_value(obj, owner_field_name):
        value = obj
        for f in owner_field_name.split('.'):
            if not value:
                break
            value = getattr(value, f, None)
        return value

    def has_object_permission(self, request, view, obj):
        has_owner_permission_func = getattr(view, 'has_owner_permission', None)
        if has_owner_permission_func:
            return view.has_owner_permission(obj)
        owner_field = getattr(view, 'owner_permission_field', 'owner')
        owner_object_func = getattr(view, 'get_owner_permission_object', None)
        owner_object = owner_object_func() if owner_object_func else request.user
        return self.__discover_owner_value(obj, owner_field) == owner_object


class IsOwnerOrReadOnlyPermission(IsOwnerPermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return super().has_object_permission(request, view, obj)


class IsMemberPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        member = getattr(request.user, 'member', None)
        return bool(member)


class IsMemberVerifiedPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        member = getattr(request.user, 'member', None)
        return bool(member) and member.is_verified


class IsMemberVerifiedOrReadOnlyPermission(IsMemberVerifiedPermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return super().has_permission(request, view)


class IsAdminOrganizationPermission(permissions.BasePermission):
    """ custom class to check permissions for sessions """

    def get_object(self, view, obj):
        get_organization_object_permission = getattr(view, 'get_organization_object_permission', None)
        if get_organization_object_permission:
            obj = get_organization_object_permission(obj)
        return obj

    def has_permission(self, request, view):
        has_organization_permission = getattr(view, 'has_organization_permission', None)
        if has_organization_permission:
            return has_organization_permission()
        return True

    def has_object_permission(self, request, view, obj):
        from apps.bycing_org.models import OrganizationMember
        obj = self.get_object(view, obj)
        return OrganizationMember.objects.filter(member=request.user.member, organization=obj, is_active=True
                                                 ).filter(Q(is_admin=True) | Q(is_master_admin=True)).exists()


class IsAdminOrganizationOrReadOnlyPermission(IsAdminOrganizationPermission):
    """ custom class to check permissions for sessions """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            # obj = self.get_object(view, obj)
            # return OrganizationMember.objects.filter(
            #     member=request.user.member, organization=obj, is_active=True).exists()
            return True
        return super().has_object_permission(request, view, obj)


    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return super().has_permission(request, view)


class NestedMultipartParser(parsers.MultiPartParser):

    def parse(self, stream, media_type=None, parser_context=None):
        result = super().parse(stream=stream, media_type=media_type, parser_context=parser_context)
        query_data = result.data
        query_data._mutable = True

        # find for a json dump. this is a trick to allow json data mixed
        json_data = query_data.get('--JSON_DATA--', None)
        if json_data:
            try:
                json_data = json.loads(json_data)
                result.data = json_data
                return result
            except Exception:
                pass

        # TODO: this will support only 1 level nested dict
        for key, value in query_data.dict().items():
            if '[' in key and ']' in key:
                # nested
                index_left_bracket = key.index('[')
                index_right_bracket = key.index(']')
                nested_dict_key = key[:index_left_bracket]
                nested_value_key = key[index_left_bracket + 1:index_right_bracket]
                query_data.pop(key)
                query_data['{}.{}'.format(nested_dict_key, nested_value_key)] = value
        return result


class CustomPagination(PageNumberPagination):
    """ Custom Pagination to be used in rest api"""

    BIG_PAGE_SIZE = 10000000
    page_size_query_param = 'page_size'

    def paginate_queryset(self, queryset, request, view=None):
        if view:
            max_page_size = getattr(view, 'max_page_size', self.max_page_size)
            if max_page_size is None:
                max_page_size = settings.REST_FRAMEWORK.get('MAX_PAGE_SIZE_DEFAULT', 100)
            self.max_page_size = self.BIG_PAGE_SIZE if max_page_size == 0 else max_page_size
        return super(CustomPagination, self).paginate_queryset(queryset, request, view=view)

    def get_page_size(self, request):
        """
        this is overrided to allow 0 as a page_size.
        if page_size=0, we will set page_size as max_page_size.
        """
        page_size = self.page_size
        if self.page_size_query_param:
            try:
                page_size = _positive_int(
                    request.query_params[self.page_size_query_param],
                    strict=False,
                    cutoff=self.max_page_size
                )
            except (KeyError, ValueError):
                pass
        if page_size == 0:
            page_size = self.max_page_size
        return page_size

    def get_paginated_response(self, data):
        """ override pagination structure in list rest api """
        next_page = self.page.next_page_number() if self.page.has_next() else None
        previous_page = self.page.previous_page_number() if \
            self.page.has_previous() else None
        return Response({
            'pagination': {
                'next_url': self.get_next_link(),
                'previous_url': self.get_previous_link(),
                'current_page': self.page.number,
                'next_page': next_page,
                'previous_page': previous_page,
                'first_page': 1,
                'last_page': self.page.paginator.num_pages,
                'page_size': self.get_page_size(self.request),
                'total': self.page.paginator.count,
            },
            'results': data
        })


class Base64ImageField(serializers.ImageField):
    def __init__(self, *args, **kwargs):
        self.max_size = kwargs.pop('max_size', settings.IMAGE_UPLOAD_MAX_SIZE)
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        if isinstance(data, list):
            data = data[0] if data else None
        if not isinstance(data, UploadedFile):
            if hasattr(data, 'read'):
                data = data.read().decode()
            if data and data.startswith('data:image'):
                fmt, imgstr = data.split(';base64,')  # fmt ~= data:image/X,
                ext = fmt.split('/')[-1]  # guess file extension
                uid = uuid.uuid4()
                data = ContentFile(base64.b64decode(imgstr), name=uid.urn[9:] + '.' + ext)

        is_link = isinstance(data, str) and (data.startswith('http://') or data.startswith('https://'))
        if (not is_link) and self.max_size and (data.size > self.max_size):
            raise ValidationError(f"Max file size is {self.max_size}B")

        return super(Base64ImageField, self).to_internal_value(data)


def split_uppercase(string):
    return re.sub(r'([a-z])([A-Z])', r'\1 \2', string)


class SetCurrentUserDefaultSerializerMixin(object):
    current_user_default_create_field = 'create_by'
    current_user_default_update_field = 'update_by'

    def get_current_user(self):
        request = self.context.get('request', None)
        return request and request.user

    def save(self, **kwargs):
        current_user = self.get_current_user()
        if current_user:
            if (self.instance and self.current_user_default_update_field) or \
                    ((not self.instance) and self.current_user_default_update_field):
                kwargs.setdefault(self.current_user_default_update_field, current_user)
            if (not self.instance) and self.current_user_default_create_field:
                kwargs.setdefault(self.current_user_default_create_field, current_user)
        return super(SetCurrentUserDefaultSerializerMixin, self).save(**kwargs)


def date_from_request(request, date_param_name, abort=True):
    date_str = request.query_params.get(date_param_name)
    if date_str:
        try:
            date = parse_date(date_str)
        except ValueError:
            date = None
        if (not date) and abort:
            raise serializers.ValidationError({date_param_name: 'Invalid date format "{}"'.format(date_str)})
        return date


def date_coerce(s):
    return (s and datetime.datetime.strptime(s, '%Y-%m-%d').date()) or None


def decimal_coerce(s):
    if s in (None, ""):
        return None
    return decimal.Decimal(s)


def time_coerce(s):
    if not s:
        return None
    format = '%H:%M' if len(s.split(':')) == 2 else '%H:%M:%S'
    return datetime.datetime.strptime(s, format).time() or None


def datetime_coerce(s):
    return (s and parse_datetime(s)) or None


def integer_safe_coerce(v):
    return int(v) if (v or v == 0) else None


def float_safe_coerce(v):
    return float(v) if (v or v == 0) else None


def number_safe_coerce(v):
    return None if (not v and v != 0) else int(v) if isinstance(v, int) else float(v)


def str_lower_coerce(v):
    return str(v).lower() if v else None


class CreateListMixin:
    """Allows bulk creation of a resource."""

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True

        return super().get_serializer(*args, **kwargs)


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    key_salt = 'AccountActivationTokenGenerator'

    def _make_hash_value(self, user, timestamp):
        return f'{user.pk}{timestamp}{user.is_active}'


account_activation_token = AccountActivationTokenGenerator()
account_password_reset_token = PasswordResetTokenGenerator()


def ex_reverse(viewname, **kwargs):
    if viewname.startswith('http://') or viewname.startswith('https://'):
        return viewname
    if kwargs.pop('drf', None):
        VERSION_PARAM = settings.REST_FRAMEWORK.get('VERSION_PARAM', 'version')
        DEFAULT_VERSION = settings.REST_FRAMEWORK.get('DEFAULT_VERSION', 'v1')
        _kwargs = kwargs.get('kwargs') or {}
        _kwargs[VERSION_PARAM] = DEFAULT_VERSION
        kwargs['kwargs'] = _kwargs

    host = kwargs.pop('hostname', None)
    request = kwargs.pop('request', None)
    scheme = kwargs.pop('scheme', None)
    if not host:
        host = request.get_host() if request else settings.HOSTNAME

    if not viewname:
        rel_path = ''
    elif viewname.startswith('/'):
        rel_path = viewname
    else:
        rel_path = reverse(viewname, **kwargs)

    if scheme == 'auto' and request:
        scheme = '{}://'.format(request.scheme)
    else:
        scheme = '{}://'.format(scheme) if (scheme and scheme != 'auto') else ''

    return '{0}{1}{2}'.format(scheme, host, rel_path)


def generate_otp_code(otp_key, length=6, interval=120, salt=None):
    if salt:
        otp_key = f'{otp_key}-{salt}'

    b32_key = base64.b32encode(otp_key.encode('u8')).decode('u8')
    otp = pyotp.TOTP(b32_key, digits=length, interval=interval)
    return otp.now()


def verify_otp_code(code, otp_key, salt=None, length=6, interval=120, valid_window=0):
    if salt:
        otp_key = f'{otp_key}-{salt}'

    b32_key = base64.b32encode(otp_key.encode('u8')).decode('u8')
    otp = pyotp.TOTP(b32_key, digits=length, interval=interval)
    return otp.verify(code, valid_window=valid_window)


def get_member_verify_otp(member, salt=None):
    from django.conf import settings
    otp_key = settings.OTP_MEMBER_VERIFY_KEY
    length = settings.OTP_MEMBER_VERIFY_CODE_LENGTH
    interval = settings.OTP_MEMBER_VERIFY_INTERVAL
    if salt:
        otp_key = f'{otp_key}-{salt}'

    otp_key = f'{otp_key}-{member.pk}'
    b32_key = base64.b32encode(otp_key.encode('u8')).decode('u8')
    return pyotp.TOTP(b32_key, digits=length, interval=interval)


class CharArrayFilter(filters.BaseCSVFilter, filters.CharFilter):
    pass
