from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.core import exceptions as django_exceptions

from wrh_organization.helpers.utils import DynamicFieldsSerializerMixin, Base64ImageField

User = get_user_model()


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(style={'input_type': 'password'})
    current_password = serializers.CharField(style={'input_type': 'password'})

    default_error_messages = {
        'invalid_password': 'Invalid Password',
    }

    def validate_current_password(self, value):
        is_password_valid = self.context['request'].user.check_password(value)
        if is_password_valid:
            return value
        else:
            self.fail('invalid_password')

    def validate_new_password(self, new_password):
        try:
            validate_password(new_password, self.context['request'].user)
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError({'new_password': list(e.messages)})
        return new_password


class SetPrefsSerializer(serializers.Serializer):
    default_regional_org = serializers.IntegerField(allow_null=True)


class PermissionSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('id', 'name', 'codename')


class NestedGroupSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(read_only=True, many=True)

    class Meta:
        model = Group
        fields = ('id', 'name', 'permissions')


class UserSessionSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    user_permissions = PermissionSerializer(read_only=True, many=True)
    groups = NestedGroupSerializer(read_only=True, many=True)

    class Meta:
        model = User
        exclude = ('password',)

    def to_representation(self, instance):
        res = super().to_representation(instance)
        if 'prefs' in res and not res['prefs']:
            res['prefs'] = {}
        return res


class SessionSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    password = serializers.CharField(max_length=128, style={'input_type': 'password'})
    remember = serializers.BooleanField(initial=False, required=False)


class UserProfileSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'gender', 'birth_date', 'avatar', 'prefs')
        read_only_fields = ('email', 'username',)

    def to_representation(self, instance):
        res = super().to_representation(instance)
        if 'prefs' in res and not res['prefs']:
            res['prefs'] = {}
        return res
