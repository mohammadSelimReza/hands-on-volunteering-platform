from rest_framework import serializers

from app.user.serializers import UserSerializer

from .models import (
    CampaignModel,
    CommentModel,
    EventModel,
    LocationModel,
    RegisterPeople,
)


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationModel
        fields = "__all__"


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegisterPeople
        fields = ["user"]


class EventSerializer(serializers.ModelSerializer):
    registered_people = RegisterSerializer(many=True, required=False)

    class Meta:
        model = EventModel
        fields = [
            "title",
            "created_by",
            "image",
            "description",
            "location",
            "category",
            "skills_required",
            "private",
            "event_id",
            "event_start",
            "event_end",
            "created_at",
            "is_available",
            "registered_people",
        ]


""""Campaign serializer"""


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentModel
        fields = ["id", "option", "created_at", "campaign", "user", "total_time"]


class CampaignSerializer(serializers.ModelSerializer):
    creator = UserSerializer()

    class Meta:
        model = CampaignModel
        fields = [
            "id",
            "creator",
            "title",
            "body",
            "image",
            "urgency_level",
            "created_at",
            "total_comments",
            "total_time_from_start",
            "total_volunteered_time",
        ]


class CampaignNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignModel
        fields = [
            "title",
        ]


class HistroySerializer(serializers.ModelSerializer):
    campaign = CampaignNameSerializer()

    class Meta:
        model = CommentModel
        fields = ["campaign", "option", "created_at", "total_time"]
