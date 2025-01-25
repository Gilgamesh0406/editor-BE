from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
import django.contrib.auth.models as auth_models
import os
from rest_framework.response import Response
from rest_framework.decorators import api_view
class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = os.getenv("CALL_BACK_URL")
    client_class = OAuth2Client
class GithubLogin(SocialLoginView):
    adapter_class = GitHubOAuth2Adapter
    callback_url = os.getenv("CALL_BACK_URL")
    client_class = OAuth2Client

@api_view(['POST'])
def check_email(request):
    email = request.data.get('email')
    if email:
        user_exists = auth_models.User.objects.filter(email=email).exists()
        return Response({'email_exists': user_exists})
    return Response({'email_exists': False})