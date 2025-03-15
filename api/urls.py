from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from app.event import views as event_view
from app.user import views as user_view

router = DefaultRouter()
router.register(r"campaigns", event_view.CampaignViewSet, basename="campaign")
router.register(r"comments", event_view.CommentViewSet, basename="comment")
urlpatterns = [
    path("", include(router.urls)),
    path("user/list/<user_id>/", user_view.UserAPIView.as_view(), name="userView"),
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
    # password:
    path(
        "user/<email>/password/reset/",
        user_view.ResetPasswordView.as_view(),
        name="passwordReset",
    ),
    path(
        "user/password/change/",
        user_view.PasswordChangeAPIView.as_view(),
        name="passwordReset",
    ),
    path(
        "user/<user_id>/password/update/",
        user_view.PasswordUpdateAPIView.as_view(),
        name="passwordUpdate",
    ),
    # profile:
    path(
        "user/<user_id>/profile/update/",
        user_view.ProfileUpdate.as_view(),
        name="profileUpdate",
    ),
    # skills and interest:
    path("skills/list/", user_view.SkillViewAPI.as_view(), name="skillsView"),
    path("interests/list/", user_view.InterestsViewAPI.as_view(), name="interestsView"),
    # event:
    path("event/create/", event_view.EventViewAPI.as_view(), name="eventView"),
    # location:
    path("event/location/", event_view.LocationApiView.as_view(), name="eventLocation"),
    path("event/register/", event_view.EventRegister.as_view(), name="eventRegister"),
]
