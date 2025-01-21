from django.urls import path
from . import views
# Create your views here.

urlpatterns = [
    path("create_chat_stream", views.create_chat_stream, name="create_chat"),
    path("get_first_chats/", views.get_first_chats, name="get_first_chats"),
    path("get_chats_by_session_id/", views.get_chats_by_session_id, name="get_chats_by_session_id"),
    path("save_chat", views.save_chat, name="save_chat"),
]