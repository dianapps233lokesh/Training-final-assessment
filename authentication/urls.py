from django.urls import path

from authentication.views import (
    LoginAPIView,
    LogoutAPIView,
    ProfileAPIView,
    UserRegistrationAPIView,
)

urlpatterns = [
    path("register/", UserRegistrationAPIView.as_view(), name="user-registration"),
    path("login/", LoginAPIView.as_view(), name="user-login"),
    path("profile/", ProfileAPIView.as_view(), name="user-profile"),
    path("logout/", LogoutAPIView.as_view(), name="user-logout"),
]
