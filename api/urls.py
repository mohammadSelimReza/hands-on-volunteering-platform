from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from app.user import views as user_view

urlpatterns = [
    path("user/list/", user_view.UserAPIView.as_view(), name="userView"),
    # registraion process:
    path(
        "user/registration/", user_view.CreateUserAPIView.as_view(), name="createUser"
    ),
    path(
        "user/activate/<uid64>/<token>/",
        user_view.activate_account,
        name="verifiedUser",
    ),
    # login token:
    path("user/token/", user_view.LoginTokenAPIView.as_view(), name="tokenAccess"),
    path("user/token/refresh", TokenRefreshView.as_view(), name="tokenRefresh"),
]
