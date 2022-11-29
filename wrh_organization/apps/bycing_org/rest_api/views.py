import csv
import decimal
import io
import traceback
from datetime import timedelta

import stripe
from django.conf import settings
from django.contrib.auth import login
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.template.loader import render_to_string
from django.utils import dateparse, timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from dynamic_preferences.registries import global_preferences_registry
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, PermissionDenied, MethodNotAllowed
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from stripe.error import StripeError

from apps.bycing_org.models import Member, Organization, User, OrganizationMember, OrganizationMemberOrg, \
    FieldsTracking, Race, RaceResult, Category, RaceSeries, RaceSeriesResult, Event, FinancialTransaction
from apps.bycing_org.rest_api.filters import MemberFilter, OrganizationFilter, OrganizationMemberFilter, \
    OrganizationMemberOrgFilter, FieldsTrackingFilter, RaceFilter, RaceResultFilter, CategoryFilter, RaceSeriesFilter, \
    RaceSeriesResultFilter, EventFilter
from apps.bycing_org.rest_api.serializers import MemberSerializer, OrganizationSerializer, SignupUserSerializer, \
    ActivationEmailSerializer, MyMemberSerializer, MemberOTPVerifySerializer, OrganizationMemberSerializer, \
    NestedMemberSerializer, UserSendRecoverPasswordSerializer, UserRecoverPasswordSerializer, \
    CsvFileImportSerializer, OrganizationMemberMyRequestsSerializer, OrganizationMemberOrgSerializer, \
    NestedOrganizationSerializer, FieldsTrackingSerializer, RaceSerializer, RaceResultSerializer, CategorySerializer, \
    RaceSeriesSerializer, RaceSeriesResultSerializer, EventSerializer, PublicMemberSerializer, \
    OrganizationJoinSerializer, MyOrganizationMemberSerializer, OrganizationPrefsSerializer, EventPrefsSerializer
from wrh_organization.helpers.utils import account_activation_token, send_sms, IsMemberVerifiedPermission, \
    IsAdminOrganizationOrReadOnlyPermission, account_password_reset_token, to_dict, IsMemberPermission, random_id, \
    APICodeException

global_pref = global_preferences_registry.manager()


class ExportViewMixin(object):
    valid_export_types = {}

    def get_export_records(self, request, *args, **kwargs):
        return self.filter_queryset(self.get_queryset())

    @action(detail=False, methods=['get'], url_path='export/(?P<export_type>.+)')
    def export(self, request, *args, **kwargs):
        export_type = kwargs.get('export_type')
        if export_type not in self.valid_export_types:
            return Response({'reason': 'Invalid export type "{}"'.format(export_type)}, status=400)

        export_method = getattr(self, self.valid_export_types.get(export_type), None)
        if not export_method:
            raise NotImplementedError
        records = self.get_export_records(request, *args, **kwargs)
        return export_method(records)


class GlobalPreferencesView(viewsets.ViewSet):
    PUBLIC_KEYS = ['site_ui__terms_of_service', 'site_ui__banner_image']
    LOGIN_REQUIRED_KEYS = []
    permission_classes = (permissions.AllowAny,)

    def get_api_val(self, pref_key):
        section, name = global_pref.parse_lookup(pref_key)
        pr = global_pref.get_db_pref(section, name)
        return pr.preference.api_repr(pr.value)

    @property
    def conf_keys(self):
        keys = self.PUBLIC_KEYS
        if self.request.user.is_authenticated:
            keys += self.LOGIN_REQUIRED_KEYS
        return keys

    def get(self, request, *args, **kwargs):
        configs = {c: self.get_api_val(c) for c in self.conf_keys}
        return Response(configs)

    def retrieve(self, request, *args, **kwargs):
        conf_key = kwargs.get('pk')
        if conf_key not in self.conf_keys:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(self.get_api_val(conf_key))

    def create(self, request, *args, **kwargs):
        # this method is a trick to show this view in api-root
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class GlobalConfView(viewsets.ViewSet):
    PUBLIC_KEYS = [
        'TIME_ZONE', 'DEFAULT_ORGANIZATION_ID'
    ]
    LOGIN_REQUIRED_KEYS = ['STRIPE_PUBLISHABLE_KEY']
    permission_classes = (permissions.AllowAny,)

    @property
    def conf_keys(self):
        keys = self.PUBLIC_KEYS
        if self.request.user.is_authenticated:
            keys += self.LOGIN_REQUIRED_KEYS
        return keys

    def get(self, request, *args, **kwargs):
        configs = {c: getattr(settings, c, None) for c in self.conf_keys}
        return Response(configs)

    def retrieve(self, request, *args, **kwargs):
        conf_key = kwargs.get('pk')
        if conf_key not in self.conf_keys:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(getattr(settings, conf_key, None))

    def create(self, request, *args, **kwargs):
        # this method is a trick to show this view in api-root
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class UserRegistrationView(viewsets.ViewSet):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = SignupUserSerializer

    def _activate_get(self, request, user, *args, **kwargs):
        return render(request, 'bycing_org/email/user_activation_confirm.html', context={'new_user': user})

    @action(detail=False, methods=['GET', 'POST'],
            url_path='activate/(?P<uid>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$')
    @transaction.atomic()
    def activate(self, request, *args, **kwargs):
        uid = kwargs.get('uid')
        token = kwargs.get('token')
        invalid_msg = 'Activation link is invalid or expired'
        try:
            uid = urlsafe_base64_decode(uid)
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError):
            return Response({'error': invalid_msg}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'User with uid does not exists'}, status=status.HTTP_404_NOT_FOUND)
        if user.is_active:
            return Response({'error': invalid_msg}, status=status.HTTP_400_BAD_REQUEST)
        if not account_activation_token.check_token(user, token):
            return Response({'error': invalid_msg}, status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'GET':
            return self._activate_get(request, user, *args, **kwargs)

        user.is_active = True
        member = getattr(user, 'member', None)
        if not member or not member.email_verified:
            existing_member = Member.objects.exclude(user=user).filter(email=user.email
                                                                       ).order_by('email_verified').first()
            member = existing_member or member

        member = Member() if member is None else member

        member.set_as_verified(user)
        user.save(update_fields=['is_active'])

        login(request, user)
        next = request.GET.get('redirect') or settings.SIGNUP_ACTIVATION_REDIRECT_URL
        return redirect(next)

    @action(detail=False, methods=['POST'],
            serializer_class=ActivationEmailSerializer)
    def resend_activation_email(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({'error': 'User with this email does not exist! please sign up first.'},
                            status=status.HTTP_404_NOT_FOUND)
        if user.is_active:
            return Response({'error': 'User with this email is already activated.'}, status=status.HTTP_409_CONFLICT)
        self._send_activation_email(user)
        return Response({'message': 'email activation sent'}, status=status.HTTP_200_OK)

    def _send_activation_email(self, user):
        subject = 'Activate Your Account'
        message = render_to_string('bycing_org/email/user_activation.html', {
            'user': user,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
            'request': self.request
        })

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], html_message=message,
                  fail_silently=False)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response({'error': 'You are already signed up'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save(is_active=False)
        self._send_activation_email(user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['POST'], serializer_class=UserSendRecoverPasswordSerializer)
    def send_recover_password(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(email=serializer.validated_data.get('email')).first()
        if not user:
            return Response({'error': 'User with this email does not exists!'}, status=status.HTTP_404_NOT_FOUND)
        if not user.is_active:
            return Response({'error': 'User with this email is inactive.'}, status=status.HTTP_403_FORBIDDEN)

        subject = 'Reset Your Password'
        message = render_to_string('bycing_org/email/user_recover_password.html', {
            'user': user,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_password_reset_token.make_token(user),
            'request': self.request
        })

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], html_message=message,
                  fail_silently=False)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _recover_password_get(self, request, user, *args, **kwargs):
        return render(request, 'bycing_org/email/user_recover_password_confirm.html', context={'new_user': user})

    @action(detail=False, methods=['GET', 'POST'], serializer_class=UserRecoverPasswordSerializer,
            url_path='recover_password/(?P<uid>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$')
    def recover_password(self, request, *args, **kwargs):
        uid = kwargs.get('uid')
        token = kwargs.get('token')
        invalid_msg = 'Reset link is invalid or expired'
        try:
            uid = urlsafe_base64_decode(uid)
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError):
            return Response({'error': invalid_msg}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'User with uid does not exists'}, status=status.HTTP_404_NOT_FOUND)
        if not user.is_active:
            return Response({'error': 'This user is inactive!'}, status=status.HTTP_400_BAD_REQUEST)
        if not account_password_reset_token.check_token(user, token):
            return Response({'error': invalid_msg}, status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'GET':
            return self._recover_password_get(request, user, *args, **kwargs)

        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data.get('new_password'))
        user.save()
        next = request.GET.get('next') or settings.LOGIN_URL
        if request.GET.get('redirect') == 'true':
            return redirect(next)
        return Response({'next': next}, status=status.HTTP_200_OK)

    create = post


class MemberView(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    filterset_class = MemberFilter
    search_fields = '__all__'
    ordering_fields = '__all__'
    ordering = ('id',)

    def _verify(self, request, member, type):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data.get('code')
        verified = member.check_verify_code(code, type=type, valid_window=settings.OTP_MEMBER_VERIFY_VALID_WINDOW)
        if not verified:
            return Response({'error': 'invalide code'}, status=status.HTTP_400_BAD_REQUEST)
        if type == 'phone':
            member.phone_verified = True
            member.save(update_fields=['phone_verified'])
        elif type == 'email':
            member.email_verified = True
            member.save(update_fields=['email_verified'])

        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET', 'PUT', 'PATCH'], permission_classes=(IsAuthenticated,),
            serializer_class=MyMemberSerializer)
    def me(self, request, *args, **kwargs):
        user = request.user
        member = getattr(user, 'member', None)
        if not member:
            return Response({'detail': 'Not registered member!'}, status=status.HTTP_404_NOT_FOUND)
        if request.method == 'GET':
            return Response(self.get_serializer(instance=member).data)

        if not member:
            member = Member(user=user, **{f: getattr(user, f) for f in Member.USER_SHARED_FIELDS})
        data = request.data

        if member.email and member.email_verified:
            data.pop('email', None)
        if member.phone and member.phone_verified:
            data.pop('phone', None)

        serializer = self.get_serializer(data=request.data, instance=member, partial=request.method == 'PATCH')
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_update_fields = []
        for f in Member.USER_SHARED_FIELDS:
            v = getattr(member, f)
            if getattr(user, f) != v:
                setattr(user, f, v)
                user_update_fields.append(f)
        if user_update_fields:
            user.save(update_fields=user_update_fields)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'], url_path='me/send_email_verify_code', permission_classes=(IsAuthenticated,))
    def send_email_verify_code(self, request, *args, **kwargs):
        me = getattr(request.user, 'member', None)
        if (not me) or (not me.email):
            return Response({'error': 'email not set in your profile'}, status=status.HTTP_404_NOT_FOUND)
        if me.email_verified:
            return Response({'error': 'email is already verified'}, status=status.HTTP_409_CONFLICT)

        code = me.generate_verify_code(type='email')
        subject = 'Verify Your Email'
        expiry = settings.OTP_MEMBER_VERIFY_INTERVAL
        message = render_to_string('bycing_org/email/member_verify_email.html', {
            'member': me,
            'code': code,
            'expiry': expiry,
            'request': self.request
        })

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [me.email], html_message=message,
                  fail_silently=False)
        return Response({'expiry': expiry}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path='me/send_phone_verify_code',
            permission_classes=(IsAuthenticated,))
    def send_phone_verify_code(self, request, *args, **kwargs):
        me = getattr(request.user, 'member', None)
        if (not me) or (not me.phone):
            return Response({'error': 'phone number not set in your profile'}, status=status.HTTP_404_NOT_FOUND)
        if me.phone_verified:
            return Response({'error': 'phone is already verified'}, status=status.HTTP_409_CONFLICT)

        code = me.generate_verify_code(type='phone')
        expiry = settings.OTP_MEMBER_VERIFY_INTERVAL
        message = render_to_string('bycing_org/sms/member_verify_phone.html', {
            'member': me,
            'code': code,
            'expiry': expiry,
            'request': self.request
        })
        send_sms(message, str(me.phone), fail_silently=False)
        return Response({'expiry': expiry}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path='me/email_verify',
            permission_classes=(IsAuthenticated,), serializer_class=MemberOTPVerifySerializer)
    def email_verify(self, request, *args, **kwargs):
        me = getattr(request.user, 'member', None)
        if (not me) or (not me.email):
            return Response({'error': 'email not set in your profile'}, status=status.HTTP_404_NOT_FOUND)
        if me.email_verified:
            return Response({'error': 'email is already verified'}, status=status.HTTP_409_CONFLICT)
        return self._verify(request, me, 'email')

    @action(detail=False, methods=['POST'], url_path='me/phone_verify',
            permission_classes=(IsAuthenticated,), serializer_class=MemberOTPVerifySerializer)
    def phone_verify(self, request, *args, **kwargs):
        me = getattr(request.user, 'member', None)
        if (not me) or (not me.phone):
            return Response({'error': 'phone number not set in your profile'}, status=status.HTTP_404_NOT_FOUND)
        if me.phone_verified:
            return Response({'error': 'phone is already verified'}, status=status.HTTP_409_CONFLICT)
        return self._verify(request, me, 'phone')

    @action(detail=False, methods=['GET'], permission_classes=(IsAuthenticated,),
            serializer_class=NestedMemberSerializer, filter_backends=(SearchFilter,),
            search_fields=['email', 'first_name', 'last_name'])
    def find(self, request, *args, **kwargs):
        search = request.GET.get('search') or ''
        if not search or len(search) < 3:
            raise ValidationError('Insufficient search keyword!')
        qs = self.filter_queryset(self.get_queryset())[:5]
        return Response({'results': self.get_serializer(qs, many=True).data})


class OrganizationView(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrganizationOrReadOnlyPermission,)
    serializer_class = OrganizationSerializer
    filterset_class = OrganizationFilter
    search_fields = ('name', 'about', 'type', 'website')
    ordering_fields = '__all__'
    ordering = ('id',)

    def get_queryset(self):
        return super().get_queryset()

    def perform_create(self, serializer):
        super().perform_create(serializer)
        OrganizationMember.objects.create(organization=serializer.instance, is_master_admin=True,
                                          member=self.request.user.member)

    def process_payment(self, org, token, price):
        if not token:
            raise APICodeException(status_code=status.HTTP_400_BAD_REQUEST, detail='payment token not provided')

        user = self.request.user
        try:
            charge = stripe.Charge.create(
                amount=int(price * 100),
                currency='usd',
                source=token,
                description='Org Membership #{}<{}> of user #{}<{}>'.format(org.id, org.name, user.id, user.username)
            )
        except StripeError as e:
            traceback.print_exc()
            raise APICodeException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail='Un-successful payment: {}'.format(e.user_message))

        payment_id = charge['id']
        FinancialTransaction.objects.create(user_id=user.id, amount=price, payment_id=payment_id,
                                            type=FinancialTransaction.TYPE_ORG_REGISTER)

    @action(detail=True, methods=['GET', 'POST'], permission_classes=(IsMemberPermission,),
            serializer_class=OrganizationJoinSerializer)
    @transaction.atomic()
    def join(self, request, *args, **kwargs):
        org = self.get_object()
        om = OrganizationMember.objects.filter(organization=org, member=request.user.member, is_active=True).first()
        if request.method == 'GET':
            if not om:
                return Response({'detail': 'Not joined'}, status=status.HTTP_404_NOT_FOUND)
            return Response({
                'is_admin': om.is_admin or om.is_master_admin, 'membership_plan': om.membership_plan,
                'member_fields': om.member_fields, 'start_date': om.start_date, 'exp_date': om.exp_date,
                'status': om.status, 'is_expired': om.is_expired(), 'is_expiring': om.is_expiring()
            })

        if om and (om.is_admin or om.is_master_admin):
            return Response({'detail': 'admin members dont need to renew membership'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        membership_plans = (org.membership_plans or [])
        org_member_uid = random_id(no_lower=True, no_digit=True)
        member_fields = data.get('member_fields')
        start_date = timezone.now().date()
        plan_id = data.get('plan_id')
        plan = plan_id and next((p for p in membership_plans if p.get('id') == plan_id), None)  # find the plan
        if not plan:
            return Response({'detail': 'Invalid membership plan'}, status=status.HTTP_400_BAD_REQUEST)
        if om:
            if om.status not in (OrganizationMember.STATUS_REJECT, OrganizationMember.STATUS_WAITING):
                start_date = max(start_date, om.exp_date)
                org_member_uid = om.org_member_uid or org_member_uid
            om.is_active = False
            om.save(update_fields=['is_active'])

        exp_date = start_date + timedelta(days=Organization.PERIODS_DAYS[plan['period']])
        plan['donation'] = decimal.Decimal(data.get('donation') or 0)
        membership_price = decimal.Decimal(plan.get('price') or 0) + plan['donation']

        new_om = OrganizationMember.objects.create(
            member=request.user.member, organization=org, start_date=start_date, exp_date=exp_date,
            member_fields=member_fields, org_member_uid=org_member_uid, membership_plan=plan
        )

        user_prefs = request.user.prefs or {}
        if (not user_prefs.get('default_regional_org')) and (org.type == Organization.TYPE_REGIONAL):
            user_prefs['default_regional_org'] = org.id
            self.request.user.prefs = user_prefs
            self.request.user.save(update_fields=['prefs'])

        if membership_price:
            token = data.get('token')
            self.process_payment(org, token, membership_price)

        return Response(OrganizationMemberSerializer(instance=new_om, context={'request': request}).data)

    @action(detail=True, methods=['GET', 'PUT'], permission_classes=(IsMemberPermission,))
    def my_member_fields(self, request, *args, **kwargs):
        org = self.get_object()
        om = OrganizationMember.objects.filter(organization=org, member=request.user.member, is_active=True).first()
        if not om:
            return Response({'detail': 'You are not a member of this organization'}, status=status.HTTP_403_FORBIDDEN)
        if request.method == 'GET':
            return Response(om.member_fields or {})
        data = request.data or {}
        om.member_fields = {**(om.member_fields or {}), **data}
        om.save()
        return Response(om.member_fields or {})

    @action(detail=True, methods=['GET', 'PUT', 'PATCH'], serializer_class=OrganizationPrefsSerializer)
    def prefs(self, request, *args, **kwargs):
        org = self.get_object()
        if request.method == 'GET':
            return Response(self.get_serializer(instance=org).to_representation(org))

        serializer = self.get_serializer(instance=org, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        org = serializer.save()
        return Response(serializer.to_representation(org))

    @action(detail=True, methods=['GET'])
    def summary(self, request, *args, **kwargs):
        org = self.get_object()
        members_count = OrganizationMember.objects.filter(is_active=True, organization=org).count()
        races_count = org.races.count()
        return Response({'members_count': members_count, 'races_count': races_count})

    @action(detail=False, methods=['GET'], permission_classes=(IsAuthenticated,),
            serializer_class=NestedOrganizationSerializer, filter_backends=(SearchFilter,),
            search_fields=['name', 'type', 'website'])
    def find(self, request, *args, **kwargs):
        search = request.GET.get('search') or ''
        if not search or len(search) < 3:
            raise ValidationError('Insufficient search keyword!')
        qs = self.filter_queryset(self.get_queryset())[:5]
        return Response({'results': self.get_serializer(qs, many=True).data})

    @action(detail=False, methods=['GET'], serializer_class=OrganizationMemberMyRequestsSerializer,
            filterset_class=OrganizationMemberFilter,
            queryset=OrganizationMember.objects.all(), permission_classes=(IsAuthenticated,))
    def my_membership_requests(self, request, *args, **kwargs):
        member = getattr(request.user, 'member', None)
        results = []
        qs = self.queryset.filter(member=member, status=OrganizationMember.STATUS_WAITING, is_active=True
                                  ).select_related('organization')
        qs = self.filter_queryset(qs)
        qs = self.paginate_queryset(qs)
        serializer = self.get_serializer(qs, many=True)
        results = serializer.data
        return self.get_paginated_response(results)

    @action(detail=False, methods=['POST'], serializer_class=OrganizationMemberMyRequestsSerializer,
            filterset_class=OrganizationMemberFilter,
            queryset=OrganizationMember.objects.all(), permission_classes=(IsAuthenticated,),
            url_path='my_membership_requests/(?P<org_member_id>[0-9]+)/(?P<review_action>accept|reject)'
            )
    def review_membership_request(self, request, *args, **kwargs):
        member = getattr(request.user, 'member', None)
        results = []
        member_status = kwargs.get('review_action')
        org_member_id = kwargs.get('org_member_id')
        qs = self.queryset.filter(member=member, status=OrganizationMember.STATUS_WAITING, is_active=True)
        r = get_object_or_404(qs, pk=org_member_id)
        r.status = member_status
        update_fields = ['status']
        if member_status == OrganizationMember.STATUS_REJECT:
            r.is_active = False
            update_fields.append('is_active')

        r.save(update_fields=update_fields)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'], permission_classes=(IsMemberPermission,))
    def my_orgs(self, request, *args, **kwargs):
        member = request.user.member
        oms = OrganizationMember.objects.filter(is_active=True, member=member).exclude(
            status__in=(OrganizationMember.STATUS_REJECT, OrganizationMember.STATUS_WAITING)
        )
        ids = []
        org_members = {}
        for om in oms:
            ids.append(om.organization_id)
            org_members[om.organization_id] = om

        qs = self.get_queryset().filter(id__in=list(ids))
        qs = self.filter_queryset(qs)
        qs = self.paginate_queryset(qs)
        serializer = self.get_serializer(qs, many=True)
        results = serializer.data
        for r in results:
            om = org_members[r['id']]
            r['membership'] = MyOrganizationMemberSerializer(instance=om, context={'request': request}).data
        return self.get_paginated_response(results)

    @action(detail=False, methods=['GET'])
    def default_org(self, request, *args, **kwargs):
        org_id = settings.DEFAULT_ORGANIZATION_ID
        org = Organization.objects.filter(pk=org_id).first()
        if not org:
            return Response({f'detail': f'Not found default organization # {org_id}'})
        return Response(self.get_serializer(instance=org).data)


class OrganizationMembershipMixin:
    org_id_kwarg = 'org_id'
    permission_classes = (IsAuthenticated, IsAdminOrganizationOrReadOnlyPermission,)
    _current_org = None

    def get_organization_object_permission(self, obj):
        return obj.organization

    def is_admin_organization(self):
        org = self.get_current_org()
        return OrganizationMember.objects.filter(member=self.request.user.member, organization=org, is_active=True
                                                 ).filter(Q(is_admin=True) | Q(is_master_admin=True)).exists()

    def has_organization_permission(self):
        if self.is_admin_organization():
            return True
        return self.request.method in permissions.SAFE_METHODS

    def get_current_org(self):
        if not self._current_org:
            org_id = self.kwargs.get(self.org_id_kwarg)
            assert org_id, f'{self.org_id_kwarg} is not specified in url pattern'
            member = self.request.user.member
            self._current_org = get_object_or_404(Organization.objects.filter(pk=org_id).filter(
                organizationmember__is_active=True, organizationmember__member=member).distinct())
        return self._current_org

    def perform_create(self, serializer):
        serializer.save(organization=self.get_current_org())


class OrganizationMemberView(OrganizationMembershipMixin, viewsets.ModelViewSet):
    queryset = OrganizationMember.objects.all()
    serializer_class = OrganizationMemberSerializer
    filterset_class = OrganizationMemberFilter
    search_fields = ('member__first_name', 'member__last_name', 'member__email', 'org_member_uid')
    ordering_fields = '__all__'
    extra_ordering_fields = {
        'name': ('member__first_name', 'member__last_name'),
    }
    ordering = ('id',)

    def get_queryset(self):
        organization = self.get_current_org()
        return super().get_queryset().filter(organization=organization).select_related('member', 'member__user')

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        organization = self.get_current_org()
        ctx['check_private_member_fields'] = True
        ctx['member_fields_schema'] = organization.member_fields_schema
        ctx['member_is_admin'] = self.is_admin_organization()
        return ctx

    def perform_destroy(self, instance):
        if instance.is_master_admin:
            raise ValidationError({'detail': 'cannot delete a master_admin record'})

        instance.delete()

    def perform_update(self, serializer):
        if serializer.instance.is_master_admin:
            serializer.validated_data['is_active'] = True
            org = self.get_current_org()
            if not OrganizationMember.objects.filter(member=self.request.user.member, organization=org, is_active=True
                                                     ).filter(is_master_admin=True).exists():
                raise ValidationError({'detail': 'cannot update a master_admin record'})

        serializer.save(member=serializer.instance.member)

    @transaction.atomic()
    def _import_csv_row(self, row):
        member_fields = [
            'first_name', 'last_name', 'gender', 'birth_date', 'phone', 'email', 'address1', 'address2', 'country',
            'city', 'state', 'zipcode',
        ]
        row = {k: (v or None) for k, v in row.items()}
        org_member_uid = row.pop('uuid', None)
        assert org_member_uid, 'uuid is required'
        start_date = dateparse.parse_date(row.pop('start_date', None) or '')
        exp_date = dateparse.parse_date(row.pop('exp_date', None) or '')

        org = self.get_current_org()
        flt = Q()
        member = None
        if row.get('email'):
            flt = flt | Q(email=row.get('email'))
        if row.get('phone'):
            flt = flt | Q(phone=row.get('phone'))
        if flt:
            member = Member.objects.filter(flt).first()

        if not member:
            org_member = OrganizationMember.objects.filter(
                organization=org, org_member_uid=org_member_uid, is_active=True).first()
            if org_member and (org_member.is_admin or org_member.is_master_admin):
                return
            if org_member:
                member = org_member.member
                org_member.is_active = False
                org_member.save()
            else:
                member = Member()
            for f in member_fields:
                if (f == 'phone' and member.phone_verified) or (f == 'email' and member.email_verified):
                    continue
                v = row.get(f, None)
                if not v:
                    continue
                if f == 'gender':
                    v = v.lower()
                setattr(member, f, v)
            member.save()
        else:
            old_org_members = OrganizationMember.objects.filter(
                Q(member=member, organization=org, is_active=True) |
                Q(org_member_uid=org_member_uid, organization=org, is_active=True))
            if old_org_members.filter(Q(is_admin=True) | Q(is_master_admin=True)).exists():
                return
            old_org_members.update(is_active=None)

        row['_member'] = {}
        for k in member_fields:
            v = row.pop(k, None)
            if not v:
                continue
            row['_member'][k] = v

        membership_status = OrganizationMember.STATUS_WAITING if member.user_id else None
        org_member = OrganizationMember.objects.get_or_create(
            member=member, organization=org, is_active=True,
            defaults=dict(org_member_uid=org_member_uid, start_date=start_date, exp_date=exp_date, member_fields=row,
                          status=membership_status)
        )
        return org_member

    @staticmethod
    def _unify_and_check_csv(csv_reader):
        field_names = csv_reader.fieldnames
        for i in range(len(field_names)):
            f = field_names[i].lower().replace('-', ' ')
            field_names[i] = '_'.join(f.split())
        missed_fields = {'uuid', 'first_name', 'last_name'} - set(field_names)
        if missed_fields:
            raise ValidationError({'detail': f'missed this fields: {missed_fields}'})

    @action(detail=False, methods=['POST'], serializer_class=CsvFileImportSerializer)
    def import_from_csv(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['file']
        decoded_file = file.read().decode()
        reader = csv.DictReader(io.StringIO(decoded_file))
        self._unify_and_check_csv(reader)

        failed = []
        successed = 0
        for row in reader:
            try:
                self._import_csv_row(row)
                successed += 1
            except Exception:
                traceback.print_exc()
                failed.append(row)

        return Response({'successed': successed, 'failed': failed}, status=status.HTTP_200_OK)


class OrganizationMemberOrgView(OrganizationMembershipMixin, viewsets.ModelViewSet):
    queryset = OrganizationMemberOrg.objects.all()
    permission_classes = (IsAuthenticated, IsAdminOrganizationOrReadOnlyPermission,)
    serializer_class = OrganizationMemberOrgSerializer
    filterset_class = OrganizationMemberOrgFilter
    search_fields = ('member_org__name',)
    ordering_fields = '__all__'
    ordering = ('id',)
    extra_ordering_fields = {
        'member_org': 'member_org__name',
    }

    def get_queryset(self):
        organization = self.get_current_org()
        return super().get_queryset().filter(organization=organization).select_related('member_org')

    def perform_update(self, serializer):
        serializer.save(member_org=serializer.instance.member_org)

    @action(detail=False, methods=['POST'], serializer_class=CsvFileImportSerializer)
    def import_from_csv(self, request, *args, **kwargs):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)


class FieldsTrackingView(viewsets.ReadOnlyModelViewSet):
    queryset = FieldsTracking.objects.all()
    serializer_class = FieldsTrackingSerializer
    filterset_class = FieldsTrackingFilter
    ordering = '-id'
    ordering_fields = '__all__'
    search_fields = ['object_repr', ]

    def get_queryset(self):
        return super().get_queryset().filter(content_type__app_label='bycing_org')


class AdminOrganizationActionsViewMixin:
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrganizationOrReadOnlyPermission,)

    def get_organization_object_permission(self, obj):
        return obj.organization

    def _check_org_permission(self, org):
        member = self.request.user.member
        if not (org and OrganizationMember.objects.filter(member=member, organization=org, is_active=True).filter(
                Q(is_admin=True) | Q(is_master_admin=True)).exists()):
            raise PermissionDenied('you dont have permission on this organization')

    def perform_create(self, serializer):
        self._check_org_permission(serializer.validated_data.get('organization'))
        serializer.save(create_by=self.request.user)

    def perform_update(self, serializer):
        self._check_org_permission(serializer.instance.organization)
        serializer.save(organization=serializer.instance.organization)

    def perform_destroy(self, instance):
        self._check_org_permission(instance.organization)
        instance.delete()


class RaceView(AdminOrganizationActionsViewMixin, viewsets.ModelViewSet):
    queryset = Race.objects.all()
    serializer_class = RaceSerializer
    filterset_class = RaceFilter
    ordering = '-id'
    ordering_fields = '__all__'
    extra_ordering_fields = {
        'event': ('event__name', 'event__start_date'),
    }
    search_fields = ['name', 'event__name']

    def get_queryset(self):
        return super().get_queryset().select_related('event')


class RaceResultView(AdminOrganizationActionsViewMixin, ExportViewMixin, viewsets.ModelViewSet):
    queryset = RaceResult.objects.all()
    serializer_class = RaceResultSerializer
    filterset_class = RaceResultFilter
    ordering = '-id'
    ordering_fields = '__all__'
    extra_ordering_fields = {
        'event': ('race__event__name', 'race__event__start_date'),
    }
    search_fields = ['rider__first_name', 'rider__last_name', 'race__name', 'more_data__first_name',
                     'more_data__last_name']

    valid_export_types = {
        'csv': 'export_csv',
    }

    def get_queryset(self):
        return super().get_queryset().select_related('race', 'rider', 'organization', 'rider__user', 'race__event')

    def export_csv(self, queryset):
        response = HttpResponse(content_type='text/csv')
        file_name = self.request.GET.get('_filename', None) or 'race-results'
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(file_name)
        fields_map = [
            ('id', 'Id'),
            ('rider', 'Rider'),
            ('race', 'Race'),
            ('place', 'Place'),
        ]
        fields = [f[0] for f in fields_map]
        writer = csv.DictWriter(response, fieldnames=fields)
        writer.writerow(dict(fields_map))
        for obj in queryset:
            row = to_dict(obj, fields=fields, fields_map=dict(
                race=lambda: str(obj.race),
                rider=lambda: obj.rider and str(obj.rider),
            ))
            if not row['rider']:
                more_data = obj.more_data or {}
                row['rider'] = '{} {}'.format(more_data.get('first_name') or '',
                                              more_data.get('last_name') or '').strip()
            writer.writerow(row)
        return response

    @transaction.atomic()
    def _import_csv_row(self, row, org, race):
        user = self.request.user
        row = {k: (v or None) for k, v in row.items()}
        uuid = row.get('uuid', None)
        assert uuid, 'uuid is required'
        place = int(row.get('place', None))

        org_member = OrganizationMember.objects.filter(is_active=True, organization=org, org_member_uid=uuid).first()
        rider_id = org_member and org_member.member_id
        if rider_id:
            r, _ = RaceResult.objects.update_or_create(rider_id=rider_id, race=race, organization=org,
                                                       defaults=dict(place=place, more_data=row, create_by=user))
        else:
            r = RaceResult.objects.filter(
                rider_id=None, race=race, organization=org, create_by=user, more_data__uuid=uuid).first()
            if not r:
                assert row.get('first_name')
                assert row.get('last_name')
                r = RaceResult(race=race, organization=org, create_by=user)
            r.place = place
            r.more_data = row
            r.save()
        return r

    @staticmethod
    def _unify_and_check_csv(csv_reader):
        field_names = csv_reader.fieldnames
        for i in range(len(field_names)):
            f = field_names[i].lower().replace('-', ' ')
            field_names[i] = '_'.join(f.split())
        missed_fields = {'uuid', 'first_name', 'last_name', 'place'} - set(field_names)
        if missed_fields:
            raise ValidationError({'detail': f'missed this fields: {missed_fields}'})

    @action(detail=False, methods=['POST'], serializer_class=CsvFileImportSerializer,
            url_path='organization/(?P<org_id>[0-9]+)/race/(?P<race_id>[0-9]+)/import_from_csv')
    def import_from_csv(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['file']
        decoded_file = file.read().decode()
        reader = csv.DictReader(io.StringIO(decoded_file))
        self._unify_and_check_csv(reader)

        failed = []
        successed = 0
        org_id = self.kwargs.get('org_id')
        assert org_id, 'org_id is not specified in url pattern'
        member = getattr(self.request.user, 'member', None)
        org = get_object_or_404(Organization.objects.filter(pk=org_id).filter(
            organizationmember__is_active=True, organizationmember__member=member).distinct())
        self._check_org_permission(org)

        race_id = self.kwargs.get('race_id')
        assert race_id, 'race_id is not specified in url pattern'
        race = get_object_or_404(Race.objects.filter(pk=race_id))

        for row in reader:
            try:
                self._import_csv_row(row, org=org, race=race)
                successed += 1
            except Exception:
                traceback.print_exc()
                failed.append(row)

        return Response({'successed': successed, 'failed': failed}, status=status.HTTP_200_OK)


class CategoryView(AdminOrganizationActionsViewMixin, viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filterset_class = CategoryFilter
    ordering = '-id'
    ordering_fields = '__all__'
    extra_ordering_fields = {
        'create_by': ('create_by__username'),
    }
    search_fields = ['title']


class RaceSeriesView(AdminOrganizationActionsViewMixin, viewsets.ModelViewSet):
    queryset = RaceSeries.objects.all()
    serializer_class = RaceSeriesSerializer
    filterset_class = RaceSeriesFilter
    ordering = '-id'
    ordering_fields = '__all__'
    search_fields = ['name']

    def get_queryset(self):
        return super().get_queryset().prefetch_related('events', 'races', 'races__event', 'categories')


class RaceSeriesResultView(AdminOrganizationActionsViewMixin, viewsets.ModelViewSet):
    queryset = RaceSeriesResult.objects.all()
    serializer_class = RaceSeriesResultSerializer
    filterset_class = RaceSeriesResultFilter
    ordering = '-id'
    ordering_fields = '__all__'
    extra_ordering_fields = {
        'rider': (('race_result__rider__first_name', 'race_result__rider__last_name')),
    }

    search_fields = ['race_result__rider__first_name', 'race_result__rider__last_name', 'race_result__race__name',
                     'race_series__name', 'category__title']

    def get_queryset(self):
        return super().get_queryset().select_related('race_series', 'race_result', 'race_result__rider',
                                                     'race_result__race', 'organization', 'race_result__rider__user')

    @transaction.atomic()
    def _import_csv_row(self, row, org, race_series):
        user = self.request.user
        row = {k: (v or None) for k, v in row.items()}
        res_id = row['id'] = int(row.get('id'))
        try:
            category_filters = {'pk': int(row.get('category'))}
        except (TypeError, ValueError):
            category_filters = {'title': row.get('category')}
        category = get_object_or_404(Category.objects.filter(organization=org, **category_filters))
        place = int(row.get('category_place'))

        race_result = get_object_or_404(RaceResult.objects.filter(pk=res_id))
        r, _ = RaceSeriesResult.objects.update_or_create(
            race_series=race_series, organization=org, race_result=race_result, category=category,
            defaults=dict(place=place, more_data=row, create_by=user))

        return r

    @staticmethod
    def _unify_and_check_csv(csv_reader):
        field_names = csv_reader.fieldnames
        for i in range(len(field_names)):
            f = field_names[i].lower().replace('-', ' ')
            field_names[i] = '_'.join(f.split())
        missed_fields = {'id', 'category', 'category_place'} - set(field_names)
        if missed_fields:
            return Response({'detail': f'missed this fields: {missed_fields}'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'], serializer_class=CsvFileImportSerializer,
            url_path='organization/(?P<org_id>[0-9]+)/race_series/(?P<race_series_id>[0-9]+)/import_from_csv')
    def import_from_csv(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['file']
        decoded_file = file.read().decode()
        reader = csv.DictReader(io.StringIO(decoded_file))
        self._unify_and_check_csv(reader)

        failed = []
        successed = 0
        org_id = self.kwargs.get('org_id')
        assert org_id, 'org_id is not specified in url pattern'
        member = getattr(self.request.user, 'member', None)
        org = get_object_or_404(Organization.objects.filter(pk=org_id).filter(
            organizationmember__is_active=True, organizationmember__member=member).distinct())
        self._check_org_permission(org)

        race_series_id = self.kwargs.get('race_series_id')
        assert race_series_id, 'race_series_id is not specified in url pattern'
        race_series = get_object_or_404(RaceSeries.objects.filter(pk=race_series_id))

        for row in reader:
            try:
                self._import_csv_row(row, org=org, race_series=race_series)
                successed += 1
            except Exception:
                traceback.print_exc()
                failed.append(row)

        return Response({'successed': successed, 'failed': failed}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'],
            url_path='standing_points/(?P<race_series_id>[0-9]+)/(?P<category_id>[0-9]+)')
    def standing_points(self, request, *args, **kwargs):
        race_series = get_object_or_404(RaceSeries.objects.filter(pk=kwargs.get('race_series_id')))
        category = get_object_or_404(Category.objects.filter(pk=kwargs.get('category_id')))
        points_map = {int(k): int(v) if v else 0 for k, v in (race_series.points_map or {}).items()}
        qs = RaceSeriesResult.objects.filter(race_series=race_series, category=category)
        try:
            org_id = int(request.GET.get('organization'))
        except (KeyError, TypeError):
            org_id = None
        if org_id:
            org = get_object_or_404(Organization.objects.filter(pk=org_id))
        result = {}
        for r in qs:
            points = points_map.get(r.place) or 0
            rider = r.race_result.rider
            rider_id = rider and rider.id
            if not rider:
                more_data = r.race_result.more_data or {}
                rider = rider_id = '{} {}'.format(more_data.get('first_name'), more_data.get('first_name'))
                rider = {'first_name': more_data.get('first_name'), 'last_name': more_data.get('last_name')}
            else:
                rider_id = rider.id
                user = rider.user
                if user:
                    user = {'id': user.id, 'username': user.username, 'avatar': user.avatar}
                rider = {
                    'first_name': rider.first_name, 'last_name': rider.last_name, 'birth_date': rider.birth_date,
                    'id': rider_id, 'user': user
                }

            res = result.setdefault(rider_id, {'rider': rider, 'points': 0})
            res['points'] += points
        result = sorted(result.values(), key=lambda x: x.get('points'), reverse=True)
        return Response({'results': result})


class EventView(AdminOrganizationActionsViewMixin, viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filterset_class = EventFilter
    ordering = '-id'
    ordering_fields = '__all__'
    search_fields = ['name', 'description', 'country', 'city', 'state']

    def get_queryset(self):
        return super().get_queryset().select_related('organization')

    @action(detail=True, methods=['GET', 'PUT', 'PATCH'], serializer_class=EventPrefsSerializer)
    def prefs(self, request, *args, **kwargs):
        event = self.get_object()
        if request.method == 'GET':
            return Response(self.get_serializer(instance=event).to_representation(event))

        serializer = self.get_serializer(instance=event, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        event = serializer.save()
        return Response(serializer.to_representation(event))


class PublicViewMixin:
    permission_classes = (AllowAny,)


class PublicMemberView(PublicViewMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Member.objects.all()
    serializer_class = PublicMemberSerializer
    filterset_class = MemberFilter
    search_fields = '__all__'
    ordering_fields = '__all__'
    ordering = ('id',)

    def list(self, request, *args, **kwargs):
        raise MethodNotAllowed('list')


class PublicOrganizationView(PublicViewMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    filterset_class = OrganizationFilter
    search_fields = ('name', 'about', 'type', 'website')
    ordering_fields = '__all__'
    ordering = ('id',)

    def list(self, request, *args, **kwargs):
        raise MethodNotAllowed('list')
