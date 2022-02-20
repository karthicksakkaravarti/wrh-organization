from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.bycing_org.models import Member, Organization, User
from wrh_organization.helpers.utils import DynamicFieldsSerializerMixin


class MemberSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = "__all__"
        read_only_fields = ('user',)


class MyMemberSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = "__all__"
        read_only_fields = ('user', 'phone_verified', 'email_verified')


class OrganizationSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = "__all__"


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
