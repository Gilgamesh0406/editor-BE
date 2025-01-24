from django.urls import path
from dj_rest_auth.jwt_auth import get_refresh_view
from dj_rest_auth.views import LoginView, LogoutView, UserDetailsView
from dj_rest_auth.registration.views import RegisterView
from rest_framework_simplejwt.views import TokenVerifyView
from auth_app.views import GoogleLogin, GithubLogin

urlpatterns = [
    # path('register/', RegisterView.as_view(), name='register'),
    # path('api/login/', LoginView.as_view(), name='login'),
    # path('api/google-login/', GoogleLoginView.as_view(), name='google_login'),
    # path('api/github-login/', GithubLoginView.as_view(), name='github_login'),
    path("registration/", RegisterView.as_view(), name="rest_register"),
    path("login/", LoginView.as_view(), name="rest_login"),
    path("logout/", LogoutView.as_view(), name="rest_logout"),
    path("user/", UserDetailsView.as_view(), name="rest_user_details"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("token/refresh/", get_refresh_view().as_view(), name="token_refresh"),
    path("socials/google/", GoogleLogin.as_view(), name="google_login"),
    path("socials/github/", GithubLogin.as_view(), name="github_login"),
]