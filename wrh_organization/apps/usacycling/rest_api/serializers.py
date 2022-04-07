from datetime import datetime

from apps.usacycling import models
from rest_framework import serializers

from wrh_organization.helpers.utils import DynamicFieldsSerializerMixin


class USACEventSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):

    class Meta:
        model = models.USACEvent
        fields = '__all__'


class USACClubTeamSerializers(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.USACClub
        fields = '__all__'


class USACClubSerializers(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    clubteam = USACClubTeamSerializers(many=True, read_only=True)

    class Meta:
        model = models.USACClub
        fields = '__all__'


class TimestampField(serializers.Field):
    def to_representation(self, value):
        # epoch = datetime(value)
        epoch = datetime.fromtimestamp(value).strftime('%Y-%m-%d')
        return epoch


class USACRiderSerializers(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    expdateroad = TimestampField()
    expdatemtn = TimestampField()

    class Meta:
        model = models.USACRider
        fields = '__all__'
