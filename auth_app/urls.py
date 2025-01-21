from django.urls import path
from .views import RegisterView, LoginView, GoogleLoginView, GithubLoginView

urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/google-login/', GoogleLoginView.as_view(), name='google_login'),
    path('api/github-login/', GithubLoginView.as_view(), name='github_login'),
]