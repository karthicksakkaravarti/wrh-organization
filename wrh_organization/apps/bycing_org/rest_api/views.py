import csv
import io
import traceback

from django.conf import settings
from django.contrib.auth import login
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect, render, get_object_or_404
from django.template.loader import render_to_string
from django.utils import dateparse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.bycing_org.models import Member, Organization, User, OrganizationMember
from apps.bycing_org.rest_api.filters import MemberFilter, OrganizationFilter, OrganizationMemberFilter
from apps.bycing_org.rest_api.serializers import MemberSerializer, OrganizationSerializer, SignupUserSerializer, \
    ActivationEmailSerializer, MyMemberSerializer, MemberOTPVerifySerializer, OrganizationMemberSerializer, \
    NestedMemberSerializer, UserSendRecoverPasswordSerializer, UserRecoverPasswordSerializer, \
    OrganizationMemberImportFromFileSerializer, OrganizationMemberMyRequestsSerializer
from wrh_organization.helpers.utils import account_activation_token, send_sms, IsMemberVerifiedPermission, \
    IsAdminOrganizationOrReadOnlyPermission, account_password_reset_token


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
        user.save()
        member = getattr(user, 'member', None)
        if member:
            flt = Q(email=member.email)
            update_fields = ['email_verified']
            if member.phone:
                flt = flt | Q(phone=member.phone)
            if not Member.objects.exclude(user=user).filter(flt).exists():
                member.is_verified = True
                update_fields.append('is_verified')
            member.email_verified = True
            member.save(update_fields=update_fields)

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
        user = User.objects.filter(is_active=True, email=serializer.validated_data.get('email')).first()
        if not user:
            return Response({'error': 'User with this email does not exists!'}, status=status.HTTP_404_NOT_FOUND)

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
    permission_classes = (IsAuthenticated, IsAdminOrganizationOrReadOnlyPermission,)
    serializer_class = OrganizationSerializer
    filterset_class = OrganizationFilter
    search_fields = ('name', 'about', 'type', 'website')
    ordering_fields = '__all__'
    ordering = ('id',)

    def get_queryset(self):
        return super().get_queryset().prefetch_related('members')

    def perform_create(self, serializer):
        super().perform_create(serializer)
        OrganizationMember.objects.create(organization=serializer.instance, is_master_admin=True,
                                          member=self.request.user.member)

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


class OrganizationMemberView(viewsets.ModelViewSet):
    org_id_kwarg = 'org_id'
    queryset = OrganizationMember.objects.all()
    permission_classes = (IsAuthenticated, IsAdminOrganizationOrReadOnlyPermission,)
    serializer_class = OrganizationMemberSerializer
    filterset_class = OrganizationMemberFilter
    search_fields = ('member__first_name', 'member__last_name', 'member__email', 'org_member_uid')
    ordering_fields = '__all__'
    extra_ordering_fields = {
        'name': ('member__first_name', 'member__last_name'),
    }
    ordering = ('id',)

    _current_org = None

    def get_organization_object_permission(self, obj):
        return obj.organization

    def has_organization_permission(self):
        org = self.get_current_org()
        if OrganizationMember.objects.filter(member=self.request.user.member, organization=org, is_active=True
                                             ).filter(Q(is_admin=True) | Q(is_master_admin=True)).exists():
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

    def get_queryset(self):
        organization = self.get_current_org()
        return super().get_queryset().filter(organization=organization).select_related('member')

    def perform_create(self, serializer):
        serializer.save(organization=self.get_current_org())

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
            flt = flt | Q(email=row.get('email'), email_verified=True)
        if row.get('phone'):
            flt = flt | Q(email=row.get('phpne'), phone_verified=True)
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
                setattr(member, f, row.get(f, None))
            member.save()
        else:
            old_org_members = OrganizationMember.objects.filter(
                Q(member=member, organization=org, is_active=True) |
                Q(org_member_uid=org_member_uid, organization=org, is_active=True))
            if old_org_members.filter(Q(is_admin=True) | Q(is_master_admin=True)).exists():
                return
            old_org_members.update(is_active=None)
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
            return Response({'detail': f'missed this fields: {missed_fields}'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'], serializer_class=OrganizationMemberImportFromFileSerializer)
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
