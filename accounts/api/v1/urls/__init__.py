from django.urls import path, include

app_name = "accounts-api-v1"
urlpatterns = [
    path("profile/", include("accounts.api.v1.urls.profile")),
    path("", include("accounts.api.v1.urls.user")),
]
