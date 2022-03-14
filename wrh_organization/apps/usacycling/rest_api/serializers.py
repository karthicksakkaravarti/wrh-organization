from datetime import datetime

from apps.usacycling import models
from rest_framework import serializers

from wrh_organization.helpers.utils import DynamicFieldsSerializerMixin


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Address
        fields = '__all__'


class DatesSerializer(serializers.ModelSerializer):
    address = AddressSerializer()

    class Meta:
        model = models.Dates
        fields = '__all__'

    def create(self, validated_data):
        address = validated_data.pop('address')
        address_ser = AddressSerializer(data=address)
        address_ser.is_valid(raise_exception=True)
        validated_data['address'] = models.Address.objects.create(**address_ser.validated_data)
        usaEvent = models.Dates.objects.create(**validated_data)
        return usaEvent


class LinkstSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Links
        fields = '__all__'


class USAEventSerializer(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    dates = DatesSerializer()
    links = LinkstSerializer()

    class Meta:
        model = models.USAEvent
        fields = '__all__'

    def create(self, validated_data):
        dates = validated_data.pop('dates')
        date_ser = DatesSerializer(data=dates)
        date_ser.is_valid(raise_exception=True)
        date_ser.save()
        validated_data['dates'] = models.Dates.objects.get(id=date_ser.data.get('id'))
        links = validated_data.pop('links')
        link_ser = LinkstSerializer(data=links)
        link_ser.is_valid()
        link_ser.save()
        validated_data['links'] = models.Links.objects.get(id=link_ser.data.get('id'))
        usaEvent = models.USAEvent.objects.get_or_create(**validated_data)
        return usaEvent


class USACyclingClubTeamsSerializers(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.USACyclingClubs
        fields = '__all__'


class USACyclingClubsSerializers(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    clubteam = USACyclingClubTeamsSerializers(many=True, read_only=True)

    class Meta:
        model = models.USACyclingClubs
        fields = '__all__'


class TimestampField(serializers.Field):
    def to_representation(self, value):
        # epoch = datetime(value)
        epoch = datetime.fromtimestamp(value).strftime('%Y-%m-%d')
        return epoch


class USARiderSerializers(DynamicFieldsSerializerMixin, serializers.ModelSerializer):
    expdateroad = TimestampField()
    expdatemtn = TimestampField()

    class Meta:
        model = models.USARider
        fields = '__all__'
