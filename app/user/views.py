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
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from _backend.settings.base import BACKEND_URL, FRONTEND_URL

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
        # Check if email already exists in the database
        # Check if the email already exists in the database
        email = request.data.get("email")
        try:
            existing_user = user_model.User.objects.get(email=email)
            if existing_user.is_active:
                # Email is already registered and active
                return Response(
                    {"error": "Email is already registered."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                # Email exists but the user is not active, so delete the user
                existing_user.delete()
                return Response(
                    {
                        "error": "User is inactive. Account deleted.Try to Register again"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except user_model.User.DoesNotExist:
            # Email does not exist in the database, continue with user creation
            pass

        # Create the user instance and validate the data
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Generate the confirmation token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.user_id))

            # Create the confirmation link
            confirm_link = f"{BACKEND_URL}/user/activate/{uid}/{token}"

            # Prepare the email subject and body
            email_subject = "Confirm your email"
            email_body = render_to_string(
                "confirm_email.html", {"confirm_link": confirm_link}
            )

            # Create the email instance
            email = EmailMultiAlternatives(email_subject, "", to=[user.email])
            email.attach_alternative(email_body, "text/html")

            # Send the email and handle potential exceptions
            try:
                email.send()
            except BadHeaderError:
                # Rollback user creation if email sending fails
                user.delete()
                return Response(
                    {"error": "Invalid email header."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except Exception as e:
                # Rollback user creation if email sending fails
                user.delete()
                return Response(
                    {"error": f"Failed to send activation email: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return Response(
                {"detail": "Check your mail to activate your account"},
                status=status.HTTP_201_CREATED,
            )

        # If serializer is invalid, return the validation errors
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
        return redirect(f"{FRONTEND_URL}/auth/sign-in")
    except Exception as e:
        # In case of any other error, log the error and redirect
        print(f"Error during account activation: {e}")
        return redirect(f"{FRONTEND_URL}/auth/sign-in")

    if user is not None and token_valid(user, token):
        # Successful activation
        user.is_active = True
        user.save()

        # Redirect to the desired page after successful activation
        return redirect(
            f"{FRONTEND_URL}/auth/sign-in/"
        )  # or any page after successful login

    else:
        # If token is invalid or expired, send an error message
        return redirect(f"{FRONTEND_URL}/auth/sign-in/?error=token_expired")


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

    def update(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id")
        password = request.data.get("password")

        if not password:
            return Response(
                {"message": "Password is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        user = get_object_or_404(user_model.User, user_id=user_id)
        user.set_password(password)
        user.otp = ""  # Reset OTP (if used for verification)
        user.save()

        return Response(
            {"message": "Password changed successfully"}, status=status.HTTP_200_OK
        )


class ProfileUpdate(generics.RetrieveUpdateAPIView):
    serializer_class = user_serializer.ProfileSerializer

    def get_object(self):
        user_id = self.kwargs["user_id"]
        return user_model.Profile.objects.get(user__user_id=user_id)

    def perform_update(self, serializer):
        profile = serializer.instance
        data = self.request.data

        # Update User first & last name if provided
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        if first_name or last_name:
            profile.user.first_name = first_name
            profile.user.last_name = last_name
            profile.full_name = f"{first_name} {last_name}"
            profile.user.full_name = f"{first_name} {last_name}"
            profile.user.save()

        # Update Profile fields if provided
        if "location" in data:
            profile.city = data["location"]
        if "personal_info" in data:
            profile.info = data["personal_info"]
        profile.save()

        # ✅ Update Skills Only if Provided
        if "skills" in data:
            skills = data["skills"]
            if skills:  # If not empty, update skills
                profile.skills.all().delete()
                user_model.ProfileSkills.objects.bulk_create(
                    [
                        user_model.ProfileSkills(profile=profile, skill_id=skill)
                        for skill in skills
                    ]
                )
            else:  # If empty list `[]`, remove all skills
                profile.skills.all().delete()

        # ✅ Update Interests Only if Provided
        if "interests" in data:
            interests = data["interests"]
            if interests:  # If not empty, update interests
                profile.causes.all().delete()
                user_model.ProfileCauses.objects.bulk_create(
                    [
                        user_model.ProfileCauses(profile=profile, cause_id=interest)
                        for interest in interests
                    ]
                )
            else:  # If empty list `[]`, remove all interests
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
