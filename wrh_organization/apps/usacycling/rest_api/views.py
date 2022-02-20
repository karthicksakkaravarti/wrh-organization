import datetime
import itertools
from datetime import timedelta

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.usacycling import models
from . import (serializers, filter)


class USAEventView(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.USAEventSerializer
    queryset = models.USAEvent.objects.all()
    filterset_class = filter.USAEventFilterFilter
    permission_classes = (IsAuthenticated,)
    search_fields = ['event_id', 'name', 'dates__address__city', 'dates__address__postal',
                     'dates__address__friendly_address']
    ordering = ('pk',)

    def date_range(self, start, end):
        delta = end - start  # as timedelta
        days = [start + timedelta(days=i) for i in range(delta.days + 1)]
        return days

    def get_queryset(self):
        query = super().get_queryset()

        if (self.request.GET.get('range_start', None) and self.request.GET.get('range_end', None)):
            temp = []
            for i in query:
                for j in self.date_range(datetime.datetime.strptime(self.request.GET.get('range_start', None), '%Y-%m-%d').date()
                        , datetime.datetime.strptime(self.request.GET.get('range_end', None), '%Y-%m-%d').date()):
                    if j in self.date_range(i.start_date, i.end_date):
                        temp.append(i.id)
            return query.filter(id__in=temp)
        return query

    @action(methods=['get'], detail=False)
    def list_labels(self, request, version):
        return Response(list(set(itertools.chain.from_iterable(
            models.USAEvent.objects.exclude(labels=None).values_list('labels', flat=True)))))


class AddressView(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.AddressSerializer
    permission_classes = (IsAuthenticated,)
    queryset = models.Address.objects.all()
    ordering = ('pk',)

    @action(methods=['get'], detail=False)
    def list_state(self, request, version):
        return Response(list(set(models.Address.objects.exclude(state=None).values_list('state', flat=True))))


class USACyclingClubsView(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.USACyclingClubsSerializers
    permission_classes = (IsAuthenticated,)
    queryset = models.USACyclingClubs.objects.all()
    search_fields = ['club_name']
    filterset_class = filter.USACyclingClubFilter
    ordering = ('pk',)

    @action(methods=['get'], detail=False)
    def list_type(self, request, version):
        return Response(
            list(set(models.USACyclingClubs.objects.values_list('club_aff_type__aff_type_description', flat=True))))


class USARiderView(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.USARiderSerializers
    permission_classes = (IsAuthenticated,)
    queryset = models.USARider.objects.all()
    search_fields = ['lastname', 'firstname', 'license']
    ordering = ('pk',)

    @action(methods=['get'], detail=False)
    def list_state(self, request, version):
        return Response(
            list(set(models.USARider.objects.exclude(state=None).exclude(state="").values_list('state', flat=True))))
