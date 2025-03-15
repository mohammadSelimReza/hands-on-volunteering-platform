from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import (
    CausesChoicesModel,
    Profile,
    ProfileCauses,
    ProfileSkills,
    SkillsModel,
    User,
)


class CustomTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["user_id"] = user.user_id
        return token


class SkillModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillsModel
        fields = ["id", "name"]


class CausesChoicesModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CausesChoicesModel
        fields = ["id", "name"]


class ProfileSkillsSerializer(serializers.ModelSerializer):
    skill = SkillModelSerializer()

    class Meta:
        model = ProfileSkills
        fields = ["skill"]


class ProfileCauseSerializer(serializers.ModelSerializer):
    cause = CausesChoicesModelSerializer()

    class Meta:
        model = ProfileCauses
        fields = ["cause"]


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "full_name",
            "image",
            "info",
            "city",
        ]


class UserSerializer(serializers.ModelSerializer):
    Profile = ProfileSerializer()
    user_skills = ProfileSkillsSerializer(many=True)
    user_interest = ProfileCauseSerializer(many=True)

    class Meta:
        model = User
        fields = [
            "user_id",
            "username",
            "first_name",
            "last_name",
            "email",
            "full_name",
            "Profile",
            "user_skills",
            "user_interest",
        ]


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    password2 = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password", "password2"]
        extra_kwargs = {"email": {"required": True, "allow_blank": False}}

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Passwords fields didn't match!"}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")  # Remove duplicate password field
        user = User.objects.create_user(
            username=validated_data["email"].split("@")[0],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        user.is_active = False  # Require email confirmation
        user.save()
        return user
