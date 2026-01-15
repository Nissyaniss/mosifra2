from django.urls import path

from .views import (
    AccountDetailView,
    AccountSpaceView,
    AdminValidationView,
    MyOffersView,
    MyStudentsView,
    tab_account,
    tab_dashboard,
    tab_offers,
    tab_students,
)

app_name = "profiles"

urlpatterns = [
    path("", AccountSpaceView.as_view(), name="account_space"),
    path("my-students/", MyStudentsView.as_view(), name="my_students"),
    path("my-offers/", MyOffersView.as_view(), name="my_offers"),
    path("admin/validation/", AdminValidationView.as_view(), name="admin_validation"),
    path("admin/account/<str:account_type>/<int:account_id>/", AccountDetailView.as_view(), name="account_detail"),
    path("htmx/tab-dashboard/", tab_dashboard, name="tab_dashboard"),
    path("htmx/tab-account/", tab_account, name="tab_account"),
    path("htmx/tab-offers/", tab_offers, name="tab_offers"),
    path("htmx/tab-students/", tab_students, name="tab_students"),
]
