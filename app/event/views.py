import django_filters
from django.db.models import Case, IntegerField, Value, When
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
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
    HistroySerializer,
    LocationSerializer,
    RegisterSerializer,
)


# Create your views here.
class LocationApiView(generics.ListAPIView):
    queryset = LocationModel.objects.all()
    serializer_class = LocationSerializer


class EventFilter(django_filters.FilterSet):
    is_available = django_filters.BooleanFilter(method="filter_is_available")

    class Meta:
        model = EventModel
        fields = ["location", "category"]  # Don't include 'is_available' here

    # def filter_is_available(self, queryset, name, value):
    #     now = timezone.now()
    #     if value is not None:
    #         # If True, filter events that are still available (event_end >= now)
    #         # If False, filter events that are no longer available (event_end < now)
    #         return (
    #             queryset.filter(event_end__gte=now)
    #             if value
    #             else queryset.filter(event_end__lt=now)
    #         )
    #     return queryset


class EventViewAPI(viewsets.ModelViewSet):
    queryset = EventModel.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = EventFilter


class CampaignPagination(pagination.PageNumberPagination):
    page_size = 100
    page_size_query_param = page_size
    max_page_size = 100


urgency_order = Case(
    When(urgency_level="Urgent", then=Value(1)),
    When(urgency_level="Medium", then=Value(2)),
    When(urgency_level="Low", then=Value(3)),
    output_field=IntegerField(),
)


# Campaign View:
class CampaignViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Campaigns (Help Requests).
    Users can create, list, retrieve, update, and delete their campaigns.
    """

    queryset = CampaignModel.objects.annotate(urgency_order=urgency_order).order_by(
        "urgency_order"
    )
    serializer_class = CampaignSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = CampaignPagination

    def create(self, request, *args, **kwargs):
        """Custom create method to handle campaign creation failures"""
        #   "created_at": "2025-03-10T19:16:07Z",
        user_id = request.data.get("user_id")
        title = request.data.get("title")
        body = request.data.get("body")
        image = request.data.get("image")
        level = request.data.get("level")

        # Validate required fields
        if not all([user_id, title, body, level]):
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
                urgency_level=level,
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
        option = request.data.get("option")
        campaign_id = request.data.get("campaign")

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

        # Check if the user already has an active "Started" comment (i.e., ongoing)
        active_comment = CommentModel.objects.filter(
            user=user, campaign=campaign, option="Started", end_at=None
        ).first()

        if option == "Stop":
            if active_comment:
                active_comment.end_at = timezone.now()  # Mark the end time
                active_comment.save()
                return Response(
                    {"message": "Contribution stopped successfully"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": "No active volunteering session found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        elif option == "Started":
            if active_comment:
                return Response(
                    {"message": "You are already contributing!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Create a new volunteering record
            comment = CommentModel.objects.create(
                campaign=campaign,
                user=user,
                option="Started",
                created_at=timezone.now(),
            )
            return Response(
                {"message": "Contribution started successfully", "id": comment.id},
                status=status.HTTP_201_CREATED,
            )

        return Response({"error": "Invalid option"}, status=status.HTTP_400_BAD_REQUEST)


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


class VolunteerHistory(generics.ListAPIView):
    serializer_class = HistroySerializer

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        user = get_object_or_404(User, user_id=user_id)
        return CommentModel.objects.filter(user=user)


class RecentPost(generics.ListAPIView):
    serializer_class = CampaignModel

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        user = get_object_or_404(User, user_id=user_id)
        return CampaignModel.objects.filter(creator=user)
