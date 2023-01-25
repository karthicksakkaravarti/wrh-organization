import requests
from django.http import HttpResponseRedirect, JsonResponse
# Create your views here.
from django.conf import settings
import base64


def authorization_request(request):
    # Create an Authorization Request
    base_url = f"https://authz.constantcontact.com/oauth2/default/v1/authorize?client_id={settings.CC_CLIENT_ID}&redirect_uri={settings.CC_REDIRECT_URL}&response_type=code&scope=contact_data%20campaign_data%20offline_access&state=235o250eddsdff"
    return HttpResponseRedirect(base_url)

def callback(request):
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
        headers={'Authorization': f"Basic {base64_string}"}
        )
        save_user_toek(request, res.json().get('access_token'))
        return HttpResponseRedirect("/#/dashboard/member-profile")

def save_user_toek(request, token):
    current_user = request.user
    current_user.more_data['cc_token'] = token
    current_user.save()

