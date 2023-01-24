import requests
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class CCContactListView(APIView):
    permission_classes = []
    def get(self, request , *args, **kwargs):
        try:
            if request.user.more_data.get('cc_token', None):
                url = f"https://api.cc.email/v3/contact_lists?include_count=true&include_membership_count=all"
                res = requests.get(url, headers={
                    'Authorization': f"Bearer {request.user.more_data['cc_token']}"
                })
                return Response(res.json())

            else:
                return Response({'detail': 'Please authenticate with CC'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({})

class CCContactListDetailView(APIView):
    permission_classes = []
    def get(self, request ,list_id,  *args, **kwargs):
        url = f"https://api.cc.email/v3/contacts?lists={list_id}"
        res = requests.get(url, headers={
            'Authorization': f"Bearer {request.user.more_data['cc_token']}"
        })
        return JsonResponse(res.json())
