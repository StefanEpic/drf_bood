from django.urls import path, include

from bood_account.views import UserActivationView

urlpatterns = [
    path(r"", include("djoser.urls")),
    path(r"", include("djoser.urls.jwt")),
    path("users/activation/<str:uid>/<str:token>/", UserActivationView.as_view(), name="get_activation"),
]
