from datetime import timedelta

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import BadHeaderError, EmailMultiAlternatives
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.timezone import now
from rest_framework import generics, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from _backend.settings.production import BACKEND_URL, FRONTEND_URL

from . import models as user_model
from . import serializers as user_serializer
from .validators import generate_random_otp


# Create your views here.
class UserAPIView(generics.ListAPIView):
    serializer_class = user_serializer.UserSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        queryset = user_model.User.objects.filter(user_id=user_id)
        return queryset


class CreateUserAPIView(generics.CreateAPIView):
    queryset = user_model.User.objects.all()
    serializer_class = user_serializer.RegistrationSerializer
    permission_classes = [AllowAny]
    authentication_classes = [SessionAuthentication]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            #
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.user_id))
            #
            confirm_link = f"{BACKEND_URL}/user/activate/{uid}/{token}"
            email_subject = "Confirm your mail"
            email_body = render_to_string(
                "confirm_email.html", {"confirm_link": confirm_link}
            )
            email = EmailMultiAlternatives(email_subject, "", to=[user.email])
            email.attach_alternative(email_body, "text/html")
            #
            try:
                email.send()
            except BadHeaderError:
                user.delete()
                return Response(
                    {"error": "Invalid email header."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except Exception:
                user.delete()
                return Response(
                    {"error": "Failed to send activation email."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return Response(
                {"detail": "Check your mail to activate your account"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def token_valid(user, token):
    token_age = now() - user.created_at
    return token_age < timedelta(minutes=10) and default_token_generator.check_token(
        user, token
    )


def activate_account(request, uid64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uid64))
        user = user_model.User.objects.get(user_id=uid)
    except user_model.User.DoesNotExist:
        return redirect(f"{FRONTEND_URL}/invalid-link")
    except Exception as e:
        Response({"detail": f"Error in activation: {e}"})
        return redirect(f"{FRONTEND_URL}/invalid-link")
    if user is not None and token_valid(user, token):
        user.is_active = True
        user.save()
        return redirect(f"{FRONTEND_URL}/auth/sign-in")
    return redirect(f"{FRONTEND_URL}")


class LoginTokenAPIView(TokenObtainPairView):
    serializer_class = user_serializer.CustomTokenSerializer
    permission_classes = [AllowAny]


#
class ResetPasswordView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = user_serializer.UserSerializer

    def get_object(self):
        email = self.kwargs["email"]
        user = (
            user_model.User.objects.only("email", "otp", "user_id")
            .filter(email=email)
            .first()
        )
        if user:
            user.otp = generate_random_otp()
            uuidb64 = user.pk
            refresh = RefreshToken.for_user(user)
            refreshToken = str(refresh.access_token)
            user.refresh = refreshToken
            user.save()
            link = f"{FRONTEND_URL}/create-new-password/?otp={user.otp}&uuidb64={uuidb64}&refresh={refreshToken}"
            merge_data = {
                "link": link,
                "username": user.username,
            }
            subject = "Password Reset Email"
            text_body = render_to_string("email/password_reset.txt", merge_data)
            html_body = render_to_string("email/password_reset.html", merge_data)

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_body,
                from_email="srreza1999@gmail.com",
                to=[user.email],
            )
            email.attach_alternative(html_body, "text/html")
            email.send()
            return user
        return None

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        if user:
            return Response(
                {
                    "message": "If this email is registered, you will receive a password reset link."
                },
                status=200,
            )
        return Response(
            {
                "message": "If this email is registered, you will receive a password reset link."
            },
            status=200,
        )


class PasswordChangeAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = user_serializer.UserSerializer

    def create(self, request, *args, **kwargs):
        otp = request.data["otp"]
        uuidb64 = request.data["uuidb64"]
        password = request.data["password"]

        user = user_model.User.objects.only("user_id").get(otp=otp, user_id=uuidb64)
        if user:
            user.set_password(password)
            user.otp = ""
            user.save()
            return Response(
                {"message": "Password Change Successfully"},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"message": "User doesn't exist"}, status=status.HTTP_404_NOT_FOUND
            )


class PasswordUpdateAPIView(generics.UpdateAPIView):
    """
    API to update user password securely.
    """

    serializer_class = user_serializer.UserSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id")
        password = request.data.get("password")

        if not password:
            return Response(
                {"message": "Password is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        user = get_object_or_404(user_model.User, user_id=user_id)
        user.set_password(password)
        user.otp = ""
        user.save()

        return Response(
            {"message": "Password changed successfully"}, status=status.HTTP_200_OK
        )


class ProfileUpdate(generics.RetrieveUpdateAPIView):
    serializer_class = user_serializer.ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs["user_id"]
        return user_model.Profile.objects.get(user__user_id=user_id)

    def perform_update(self, serializer):
        profile = serializer.instance
        data = self.request.data

        first_name = data.get("first_name")
        last_name = data.get("last_name")
        if first_name or last_name:
            profile.user.first_name = first_name
            profile.user.last_name = last_name
            profile.full_name = f"{first_name} {last_name}"
            profile.user.full_name = f"{first_name} {last_name}"
            profile.user.save()

        if "location" in data:
            profile.city = data["location"]
        if "personal_info" in data:
            profile.info = data["personal_info"]
        profile.save()

        if "skills" in data:
            skills = data["skills"]
            if skills:
                profile.skills.all().delete()
                user_model.ProfileSkills.objects.bulk_create(
                    [
                        user_model.ProfileSkills(profile=profile, skill_id=skill)
                        for skill in skills
                    ]
                )
            else:
                profile.skills.all().delete()

        if "interests" in data:
            interests = data["interests"]
            if interests:
                profile.causes.all().delete()
                user_model.ProfileCauses.objects.bulk_create(
                    [
                        user_model.ProfileCauses(profile=profile, cause_id=interest)
                        for interest in interests
                    ]
                )
            else:
                profile.causes.all().delete()

        serializer.save()


#
class SkillViewAPI(generics.ListAPIView):
    queryset = user_model.SkillsModel.objects.all()
    serializer_class = user_serializer.SkillModelSerializer
    permission_classes = [AllowAny]


class InterestsViewAPI(generics.ListAPIView):
    queryset = user_model.CausesChoicesModel.objects.all()
    serializer_class = user_serializer.CausesChoicesModelSerializer
    permission_classes = [AllowAny]
