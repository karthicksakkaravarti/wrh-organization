from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.bycing_org.models import Member, Organization, User, OrganizationMember
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


class NestedMemberSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ('id', 'first_name', 'last_name', 'gender', 'email')


class OrganizationMemberSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    _member = NestedMemberSerializer(read_only=True, source='member')

    class Meta:
        model = OrganizationMember
        fields = "__all__"
        read_only_fields = ('is_master_admin', 'organization')


class OrganizationSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    members = NestedMemberSerializer(read_only=True, many=True)

    class Meta:
        model = Organization
        fields = "__all__"
        read_only_fields = ('verified', 'members', 'member_orgs',)


class SignupMemberSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ('phone', 'address1', 'address2', 'country', 'city', 'state', 'zipcode')
        extra_kwargs = {
            # 'phone': {'validators': []}
        }

    def __init__(self, *args, **kwargs):
        self.fields['phone'].validators = [
            v for v in self.fields['phone'].validators if not isinstance(v, UniqueValidator)
        ]
        super().__init__(*args, **kwargs)


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
        user = super().create(validated_data)
        try:
            validate_password(password, self.context['request'].user)
        except ValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        user.set_password(password)
        user.save()
        member_data.update(first_name=user.first_name, last_name=user.last_name, gender=user.gender,
                           birth_date=user.birth_date, user=user)
        member = Member.objects.update_or_create(
            defaults=member_data,
            email=user.email
        )
        return user


class MemberOTPVerifySerializer(serializers.Serializer):
    code = serializers.RegexField('[0-9]+', max_length=12, required=True, allow_null=False)
