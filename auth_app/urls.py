from django.urls import path
from dj_rest_auth.jwt_auth import get_refresh_view
from dj_rest_auth.views import LoginView, LogoutView, UserDetailsView
from dj_rest_auth.registration.views import RegisterView
from rest_framework_simplejwt.views import TokenVerifyView
from auth_app.views import GoogleLogin, GithubLogin
from auth_app.views import check_email
from allauth.account.views import ConfirmEmailView

urlpatterns = [
    # path('register/', RegisterView.as_view(), name='register'),
    # path('api/login/', LoginView.as_view(), name='login'),
    # path('api/google-login/', GoogleLoginView.as_view(), name='google_login'),
    # path('api/github-login/', GithubLoginView.as_view(), name='github_login'),
    path("registration/", RegisterView.as_view(), name="rest_register"),
    path('registration/verify-email/', RegisterView.as_view(), name='account_confirm_email'),
    path("login/", LoginView.as_view(), name="rest_login"),
    path("logout/", LogoutView.as_view(), name="rest_logout"),
    path("user/", UserDetailsView.as_view(), name="rest_user_details"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("token/refresh/", get_refresh_view().as_view(), name="token_refresh"),
    path("socials/google/", GoogleLogin.as_view(), name="google"),
    path("socials/github/", GithubLogin.as_view(), name="github"),
    path("account/check-email/", check_email, name="account_check_email"),
]