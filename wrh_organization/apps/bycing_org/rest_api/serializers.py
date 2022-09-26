from django.contrib.auth.password_validation import validate_password
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import transaction
from rest_framework import serializers

from apps.bycing_org.models import Member, Organization, User, OrganizationMember, OrganizationMemberOrg, \
    FieldsTracking, Race, RaceResult, Category, RaceSeries, RaceSeriesResult, Event
from wrh_organization.helpers.utils import DynamicFieldsSerializerMixin, Base64ImageField


class MemberSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    summary = serializers.SerializerMethodField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    extra_fields = ['summary', 'more_data']

    def get_summary(self, obj):
        race_results_count = obj.race_results.count()
        races_count = obj.race_results.distinct('race').count()
        events_count = obj.race_results.distinct('race__event').count()
        return {'races_count': races_count, 'events_count': events_count, 'race_results_count': race_results_count}

    class Meta:
        model = Member
        fields = "__all__"
        read_only_fields = ('user',)


class PublicMemberSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    summary = serializers.SerializerMethodField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    extra_fields = ['summary', 'more_data']

    def get_summary(self, obj):
        race_results_count = obj.race_results.count()
        races_count = obj.race_results.distinct('race').count()
        events_count = obj.race_results.distinct('race__event').count()
        return {'races_count': races_count, 'events_count': events_count, 'race_results_count': race_results_count}

    class Meta:
        model = Member
        exclude = ('phone', 'phone_verified', 'email', 'email_verified', 'address1', 'address2', 'zipcode', 'more_data', 'birth_date')
        read_only_fields = ('user',)


class UserMyMemberSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('id', 'avatar', 'username')
        read_only_fields = ('id', 'username')


class MyMemberSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    user = UserMyMemberSerializer(allow_null=True, required=False)
    email = serializers.EmailField(allow_null=True, required=False)
    summary = serializers.SerializerMethodField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    extra_fields = ['summary', 'more_data']

    def get_summary(self, obj):
        race_results_count = obj.race_results.count()
        races_count = obj.race_results.distinct('race').count()
        events_count = obj.race_results.distinct('race__event').count()
        return {'races_count': races_count, 'events_count': events_count, 'race_results_count': race_results_count}

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
        fields = ('id', 'username', 'avatar')


class NestedMemberSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    _user = NestedUserAvatarSerializer(source='user', read_only=True)

    class Meta:
        model = Member
        fields = ('id', 'first_name', 'last_name', 'gender', 'email', 'phone', 'address1', 'address2', 'country',
                  'city', 'state', 'zipcode', 'weight', 'height',  '_user')

    def to_representation(self, instance):
        res = super().to_representation(instance)
        if not res['_user']:
            res['_user'] = {}
        return res


class NestedMember2Serializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    _user = NestedUserAvatarSerializer(source='user', read_only=True)

    class Meta:
        model = Member
        fields = ('id', 'first_name', 'last_name', 'gender',  '_user')

    def to_representation(self, instance):
        res = super().to_representation(instance)
        if not res['_user']:
            res['_user'] = {}
        return res


class NestedOrganizationSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):

    class Meta:
        model = Organization
        exclude = ('members', 'member_orgs', 'member_fields_schema')


class NestedOrganizationShortSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = ('id', 'name', 'type')


class OrganizationSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    # members = NestedMemberSerializer(read_only=True, many=True)
    logo = Base64ImageField(required=False, allow_null=True)
    my_level = serializers.SerializerMethodField()
    extra_fields = ['member_fields_schema', 'my_level']

    def get_my_level(self, obj):
        request = self.context.get('request', None)
        level = {'is_member': None, 'is_admin': None}
        if request and request.user and getattr(request.user, 'member', None):
            r = OrganizationMember.objects.filter(organization=obj, member=request.user.member, is_active=True).first()
            level['is_member'] = True if r else False
            level['is_admin'] = True if (r and r.is_admin) else False
        return level

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
        user.more_data = {'member_data': member_data}
        user.save()
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


class NestedContentTypeSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = ['id', 'model']


class NestedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username',)


class FieldsTrackingSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):

    _user = NestedUserSerializer(read_only=True, source='user')
    _content_type = NestedContentTypeSerializer(read_only=True, source='content_type')

    class Meta:
        model = FieldsTracking
        fields = '__all__'


class NestedEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'name', 'start_date', 'end_date')


class RaceSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    extra_fields = ['more_data']

    _event = NestedEventSerializer(read_only=True, source='event')

    class Meta:
        model = Race
        fields = '__all__'
        extra_kwargs = {
            'organization': {'required': True},
            'create_by': {'read_only': True},
        }


class RaceResultSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    extra_fields = ['more_data', '_race.more_data']

    _rider = NestedMember2Serializer(read_only=True, source='rider')
    _race = RaceSerializer(read_only=True, source='race')

    class Meta:
        model = RaceResult
        fields = '__all__'
        extra_kwargs = {
            'organization': {'required': True},
            'create_by': {'read_only': True},
        }

    def to_representation(self, instance):
        res = super().to_representation(instance)
        if 'more_data' in res and not res['more_data']:
            res['more_data'] = {}
        return res


class CategorySerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):

    _create_by = NestedUserAvatarSerializer(source='create_by', read_only=True)

    class Meta:
        model = Category
        fields = '__all__'
        extra_kwargs = {
            'create_by': {'read_only': True},
        }


class NestedCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'title',)


class RaceSeriesSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    _events = NestedEventSerializer(read_only=True, source='events', many=True)
    _races = RaceSerializer(read_only=True, source='races', many=True)
    _categories = NestedCategorySerializer(read_only=True, source='categories', many=True)

    class Meta:
        model = RaceSeries
        fields = '__all__'
        extra_kwargs = {
            'create_by': {'read_only': True},
        }


class NestedRaceSeriesSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):

    class Meta:
        model = RaceSeries
        fields = ['id', 'name']


class NestedRaceResultSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):

    _rider = NestedMember2Serializer(read_only=True, source='rider')
    _race = RaceSerializer(read_only=True, source='race')

    class Meta:
        model = RaceResult
        fields = ['id', '_rider', '_race', 'more_data']


class RaceSeriesResultSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    extra_fields = ['more_data']

    _race_result = NestedRaceResultSerializer(read_only=True, source='race_result')
    _race_series = NestedRaceSeriesSerializer(read_only=True, source='race_series')
    _category = NestedCategorySerializer(read_only=True, source='category')

    class Meta:
        model = RaceSeriesResult
        fields = '__all__'
        extra_kwargs = {
            'organization': {'required': True},
            'create_by': {'read_only': True},
        }

    def to_representation(self, instance):
        res = super().to_representation(instance)
        if 'more_data' in res and not res['more_data']:
            res['more_data'] = {}
        return res


class EventSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    logo = Base64ImageField(required=False, allow_null=True)
    summary = serializers.SerializerMethodField(read_only=True)
    _organization = NestedOrganizationShortSerializer(read_only=True, source='organization')

    extra_fields = ['summary', 'more_data']

    def get_summary(self, obj):
        races_count = obj.races.count()
        race_series_count = obj.race_series.count()
        return {'races_count': races_count, 'race_series_count': race_series_count}

    class Meta:
        model = Event
        fields = '__all__'
        extra_kwargs = {
            'organization': {'required': True},
            'create_by': {'read_only': True},
        }
