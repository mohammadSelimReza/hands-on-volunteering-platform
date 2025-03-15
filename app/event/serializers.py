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
    location = LocationSerializer(read_only=True)
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
        fields = "__all__"


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
            "target",
            "urgency_level",
            "total_target",
            "collected",
            "progress_percentage",
            "created_at",
            "updated_at",
            "collection_remaining",
            "progress_percentage",
            "comment_list",
        ]
