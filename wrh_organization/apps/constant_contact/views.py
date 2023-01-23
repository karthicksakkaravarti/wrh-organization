import requests
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
# Create your views here.
from django.conf import settings


def authorization_request(request):
    # Create an Authorization Request
    base_url = f"https://authz.constantcontact.com/oauth2/default/v1/authorize?client_id={settings.CC_CLIENT_ID}&redirect_uri={settings.CC_REDIRECT_URL}&response_type=code&scope=contact_data%20campaign_data%20offline_access&state=235o250eddsdff"
    return HttpResponseRedirect(base_url)

def callback(request):
    import base64
    message_bytes = f"{str(settings.CC_CLIENT_ID)}:{str(settings.CC_CLIENT_SECRET)}".encode('ascii')

    base64_bytes = base64.b64encode(message_bytes)
    base64_string = base64_bytes.decode("ascii")

    code = request.GET.get('code', None)
    if code:
        url = f"https://authz.constantcontact.com/oauth2/default/v1/token"
        res = requests.post(url, data={
            'code': code,
            'redirect_uri': settings.CC_REDIRECT_URL,
            'grant_type': 'authorization_code'
        },
                            headers={
                                'Authorization': f"Basic {base64_string}"

                            }
                            )
        return JsonResponse(get_all_contact_list(res.json().get('access_token')))


def get_all_contact_list(token):
    url = f"https://api.cc.email/v3/contact_lists?include_count=true&include_membership_count=all"
    res = requests.get(url, headers={
        'Authorization': f"Bearer {token}"
    })
    return res.json()