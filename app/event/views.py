from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, pagination, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from app.user.models import User

from .models import (
    CampaignModel,
    CommentModel,
    EventModel,
    LocationModel,
    RegisterPeople,
)
from .serializers import (
    CampaignSerializer,
    CommentSerializer,
    EventSerializer,
    LocationSerializer,
    RegisterSerializer,
)


# Create your views here.
class LocationApiView(generics.ListAPIView):
    queryset = LocationModel.objects.all()
    serializer_class = LocationSerializer


class EventViewAPI(generics.ListCreateAPIView):
    queryset = EventModel.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]


class CampaignPagination(pagination.PageNumberPagination):
    page_size = 100
    page_size_query_param = page_size
    max_page_size = 100


# Campaign View:
class CampaignViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Campaigns (Help Requests).
    Users can create, list, retrieve, update, and delete their campaigns.
    """

    queryset = CampaignModel.objects.all().order_by("-created_at")
    serializer_class = CampaignSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = CampaignPagination

    def create(self, request, *args, **kwargs):
        """Custom create method to handle campaign creation failures"""

        user_id = request.data.get("user_id")
        title = request.data.get("title")
        body = request.data.get("body")
        image = request.data.get("image")
        level = request.data.get("level")
        total_target = request.data.get("total_target")

        # Validate required fields
        if not all([user_id, title, body, level, total_target]):
            return Response(
                {"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Validate user
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Create Campaign
        try:
            campaign = CampaignModel.objects.create(
                creator=user,
                title=title,
                body=body,
                image=image,
                target=total_target,
                urgency_level=level,
                total_target=total_target,
            )
            campaign.save()

            return Response(
                {"message": "Campaign created successfully"},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {"error": f"Campaign creation failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"], url_path="urgent")
    def urgent_campaigns(self, request):
        """Get all urgent campaigns"""
        urgent_campaigns = CampaignModel.objects.filter(urgency_level="urgent")
        serializer = self.get_serializer(urgent_campaigns, many=True)
        return Response(serializer.data)
        """Custom endpoint to fetch only urgent campaigns"""
        urgent_campaigns = CampaignModel.objects.filter(urgency_level="urgent")
        serializer = self.get_serializer(urgent_campaigns, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Comments on campaigns.
    Users can create, list, and delete their own comments.
    """

    queryset = CommentModel.objects.all().order_by("-created_at")
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        user_id = request.data.get("user")
        collected = request.data.get("collected")
        campaign_id = request.data.get("campaign")
        comment_text = request.data.get("text")
        print(user_id)
        # Validate user
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Validate campaign
        try:
            campaign = CampaignModel.objects.get(id=campaign_id)
        except CampaignModel.DoesNotExist:
            return Response(
                {"error": "Campaign not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Validate collected amount
        if collected < 0:
            return Response(
                {"error": "Collected amount cannot be negative"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        remaining_target = campaign.total_target - campaign.collected
        if collected > remaining_target:
            return Response(
                {"error": "Contribution exceeds the remaining target"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            # Update campaign's collected amount
            campaign.collected += collected
            campaign.save()

            # Create comment
            comment = CommentModel.objects.create(
                campaign=campaign,
                user=user,
                text=comment_text,
                collected=collected,
            )

        return Response(
            {"message": "Comment created successfully"},
            status=status.HTTP_201_CREATED,
        )


class EventRegister(generics.CreateAPIView):
    queryset = RegisterPeople.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        event_id = request.data.get("event_id")
        if not user_id or not event_id:
            return Response(
                {"message": "User ID and Event ID are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = get_object_or_404(User, user_id=user_id)
        event = get_object_or_404(EventModel, event_id=event_id)
        if RegisterPeople.objects.filter(user=user, event=event).exists():
            return Response(
                {"message": "User is already registered for this event"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        RegisterPeople.objects.create(user=user, event=event, registered_status=True)

        return Response(
            {"message": "Successfully Registered For This Event"},
            status=status.HTTP_201_CREATED,
        )
