from datetime import timedelta

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import BadHeaderError, EmailMultiAlternatives
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.timezone import now
from rest_framework import generics, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from _backend.settings.base import BACKEND_URL, FRONTEND_URL

from . import models as user_model
from . import serializers as user_serializer


# Create your views here.
class UserAPIView(generics.ListAPIView):
    queryset = user_model.User.objects.all()
    serializer_class = user_serializer.UserSerializer
    permission_classes = [AllowAny]


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
    print("uid64", uid64)
    print("token:", token)
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
        return redirect(f"{FRONTEND_URL}/login")
    return redirect(f"{FRONTEND_URL}")


class LoginTokenAPIView(TokenObtainPairView):
    serializer_class = user_serializer.CustomTokenSerializer
    permission_classes = [AllowAny]
