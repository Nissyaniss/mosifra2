from django.urls import path

from .views import InvitationUploadView, download_csv_model, preview_csv

app_name = "invitations"

urlpatterns = [
    path("upload/", InvitationUploadView.as_view(), name="upload"),
    path("preview/", preview_csv, name="preview"),
    path("model/", download_csv_model, name="model"),
]
