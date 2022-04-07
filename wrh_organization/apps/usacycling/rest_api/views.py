import datetime
import itertools
from datetime import timedelta

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.usacycling import models
from . import (serializers, filter)


class USACEventView(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.USACEventSerializer
    queryset = models.USACEvent.objects.all()
    filterset_class = filter.USACEventFilter
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
            models.USACEvent.objects.exclude(labels=None).values_list('labels', flat=True)))))


class USACClubView(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.USACClubSerializers
    permission_classes = (IsAuthenticated,)
    queryset = models.USACClub.objects.all()
    search_fields = ['club_name']
    filterset_class = filter.USACyclingClubFilter
    ordering = ('pk',)

    @action(methods=['get'], detail=False)
    def list_type(self, request, version):
        result = list(models.USACClub.objects.values_list('club_aff_type__aff_type_description', flat=True).distinct())
        return Response(result)


class USACRiderView(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.USACRiderSerializers
    permission_classes = (IsAuthenticated,)
    queryset = models.USACRider.objects.all()
    search_fields = ['lastname', 'firstname', 'license']
    ordering = ('pk',)

    @action(methods=['get'], detail=False)
    def list_state(self, request, version):
        return Response(
            list(set(models.USACRider.objects.exclude(state=None).exclude(state="").values_list('state', flat=True))))
