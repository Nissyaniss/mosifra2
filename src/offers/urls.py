from django.urls import path

from .views import (
    CreateOfferView,
    EditOfferView,
    OfferDetailView,
    OffersListView,
    PublicOfferDetailView,
)

app_name = "offers"

urlpatterns = [
    path("", OffersListView.as_view(), name="list"),
    path("<uuid:pk>/", PublicOfferDetailView.as_view(), name="detail_public"),
    path("create/", CreateOfferView.as_view(), name="create"),
    path("<uuid:offer_id>/view/", OfferDetailView.as_view(), name="detail"),
    path("<uuid:offer_id>/edit/", EditOfferView.as_view(), name="edit"),
]
