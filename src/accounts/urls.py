from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import (
    InvitationAcceptView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegisterSelectView,
    RegisterStudentInfoView,
    RegisterView,
    SimpleLoginView,
    TwoFactorView,
)

app_name = "accounts"

urlpatterns = [
    path("login/", SimpleLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="home"), name="logout"),
    path("register/select/", RegisterSelectView.as_view(), name="register_select"),
    path("register/student-info/", RegisterStudentInfoView.as_view(), name="register_student_info"),
    path("register/", RegisterView.as_view(), name="register"),
    path("two-factor/", TwoFactorView.as_view(), name="two_factor"),
    path("password-reset/", PasswordResetRequestView.as_view(), name="password_reset_request"),
    path("password-reset/confirm/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("invitation/<str:token>/", InvitationAcceptView.as_view(), name="invitation_accept"),
]
