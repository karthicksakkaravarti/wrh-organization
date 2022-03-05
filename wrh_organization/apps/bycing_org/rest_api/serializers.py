from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.bycing_org.models import Member, Organization, User, OrganizationMember, OrganizationMemberOrg
from wrh_organization.helpers.utils import DynamicFieldsSerializerMixin, Base64ImageField


class MemberSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = "__all__"
        read_only_fields = ('user',)


class UserMyMemberSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('id', 'avatar', 'username')
        read_only_fields = ('id', 'username')


class MyMemberSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    user = UserMyMemberSerializer(allow_null=True, required=False)

    class Meta:
        model = Member
        fields = "__all__"
        read_only_fields = ('user', 'phone_verified', 'email_verified')

    @transaction.atomic()
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        if user_data:
            user = instance.user
            for k, v in user_data.items():
                setattr(user, k, v)
            user.save(update_fields=list(user_data.keys()))
        return super().update(instance, validated_data)


class NestedUserAvatarSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'avatar')


class NestedMemberSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    _user = NestedUserAvatarSerializer(source='user', read_only=True)

    class Meta:
        model = Member
        fields = ('id', 'first_name', 'last_name', 'gender', 'email', '_user')

    def to_representation(self, instance):
        res = super().to_representation(instance)
        if not res['_user']:
            res['_user'] = {}
        return res


class NestedOrganizationSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):

    class Meta:
        model = Organization
        exclude = ('members', 'member_orgs', 'member_fields_schema')


class OrganizationSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    # members = NestedMemberSerializer(read_only=True, many=True)
    logo = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Organization
        exclude = ('members', 'member_orgs')
        read_only_fields = ('verified', 'members', 'member_orgs',)


class CsvFileImportSerializer(serializers.Serializer):
    file = serializers.FileField(required=True, validators=[FileExtensionValidator(allowed_extensions=['csv'])])


class OrganizationMemberSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    _member = NestedMemberSerializer(read_only=True, source='member')
    org_member_uid = serializers.CharField(required=True, allow_null=False, allow_blank=False)

    def validate(self, attrs):
        start_date = attrs.get('start_date') or (self.instance and self.instance.start_date)
        exp_date = attrs.get('exp_date') or (self.instance and self.instance.exp_date)
        if start_date and exp_date and (start_date > exp_date):
            raise serializers.ValidationError({"exp_date": "Exp date must be after start date"})
        return attrs

    class Meta:
        model = OrganizationMember
        fields = "__all__"
        read_only_fields = ('is_master_admin', 'organization', 'membership_price', 'status')


class OrganizationMemberMyRequestsSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    _organization = OrganizationSerializer(read_only=True, source='organization')

    class Meta:
        model = OrganizationMember
        fields = "__all__"


class OrganizationMemberOrgSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    _member_org = NestedOrganizationSerializer(read_only=True, source='member_org')

    def validate(self, attrs):
        start_date = attrs.get('start_date') or (self.instance and self.instance.start_date)
        exp_date = attrs.get('exp_date') or (self.instance and self.instance.exp_date)
        if start_date and exp_date and (start_date > exp_date):
            raise serializers.ValidationError({"exp_date": "Exp date must be after start date"})
        return attrs

    class Meta:
        model = OrganizationMemberOrg
        fields = "__all__"
        read_only_fields = ('organization', 'membership_price', 'status')


class SignupMemberSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ('phone', 'address1', 'address2', 'country', 'city', 'state', 'zipcode')


class ActivationEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(allow_null=False, required=True, allow_blank=False)


class SignupUserSerializer(serializers.ModelSerializer):
    member = SignupMemberSerializer(allow_null=True, required=False)

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name', 'birth_date', 'gender', 'member')
        extra_kwargs = {
            'password': {'write_only': True, 'required': True, 'style': {'input_type': 'password'}},
            'first_name': {'required': True, 'allow_null': False, 'allow_blank': False},
            'last_name': {'required': True, 'allow_null': False, 'allow_blank': False},
            'birth_date': {'required': True, 'allow_null': False},
        }

    @transaction.atomic()
    def create(self, validated_data):
        member_data = validated_data.pop('member', {})
        password = validated_data.pop('password')
        validated_data['username'] = validated_data.get('email')
        try:
            validate_password(password)
        except ValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        member_data.update(first_name=user.first_name, last_name=user.last_name, gender=user.gender,
                           birth_date=user.birth_date, user=user, email=user.email)
        Member.objects.create(**member_data)
        # member = Member.objects.update_or_create(
        #     defaults=member_data,
        #     email=user.email
        # )
        return user


class MemberOTPVerifySerializer(serializers.Serializer):
    code = serializers.RegexField('[0-9]+', max_length=12, required=True, allow_null=False)


class UserSendRecoverPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, allow_null=False, allow_blank=False)


class UserRecoverPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(style={'input_type': 'password'})

    def validate_new_password(self, new_password):
        try:
            validate_password(new_password, self.context['request'].user)
        except ValidationError as e:
            raise serializers.ValidationError({'new_password': list(e.messages)})
        return new_password
