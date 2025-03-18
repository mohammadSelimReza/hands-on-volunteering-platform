from datetime import datetime

import django_filters
from django.db.models import Case, IntegerField, Value, When
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from rest_framework import generics, pagination, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from app.user.models import Profile, User

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


# Location API
class LocationApiView(generics.ListAPIView):
    queryset = LocationModel.objects.all()
    serializer_class = LocationSerializer


# Filtering for Events
class EventFilter(django_filters.FilterSet):
    is_available = django_filters.BooleanFilter(method="filter_is_available")

    class Meta:
        model = EventModel
        fields = ["location", "category"]

    def filter_is_available(self, queryset, name, value):
        now = timezone.now()
        return (
            queryset.filter(event_end__gte=now)
            if value
            else queryset.filter(event_end__lt=now)
        )


# Event View API
class EventViewAPI(viewsets.ModelViewSet):
    queryset = EventModel.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = EventFilter


# Pagination for Campaigns
class CampaignPagination(pagination.PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 100


# Ordering Campaigns by Urgency
urgency_order = Case(
    When(urgency_level="Urgent", then=Value(1)),
    When(urgency_level="Medium", then=Value(2)),
    When(urgency_level="Low", then=Value(3)),
    output_field=IntegerField(),
)


# Campaign ViewSet
class CampaignViewSet(viewsets.ModelViewSet):
    """
    To Create you need to pass these following data:
    {
        "user_id":"user_id",
        "title":"title",
        "body":"details",
        "image":"url_field(optional)",
        "level": "Low / Medium / Urgent"
    }
    This post request will create a new campaign post.
    """

    queryset = CampaignModel.objects.annotate(urgency_order=urgency_order).order_by(
        "urgency_order"
    )
    serializer_class = CampaignSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = CampaignPagination

    def create(self, request, *args, **kwargs):
        """
        To Create you need to pass these following data:
        {
            "user_id":"user_id",
            "title":"title",
            "body":"details",
            "image":"url_field(optional)",
            "level": "Low / Medium / Urgent"
        }
        This post request will create a new campaign post.
        """

        user_id = request.data.get("user_id")
        title = request.data.get("title")
        body = request.data.get("body")
        image = request.data.get("image")
        level = request.data.get("level")

        if not all([user_id, title, body, level]):
            return Response(
                {"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST
            )

        user = get_object_or_404(User, user_id=user_id)

        campaign = CampaignModel.objects.create(
            creator=user,
            title=title,
            body=body,
            image=image,
            urgency_level=level,
        )

        return Response(
            {"message": "Campaign created successfully"}, status=status.HTTP_201_CREATED
        )

    def list(self, request, *args, **kwargs):
        """Update volunteer points whenever campaigns are fetched in the feed."""
        print("access to it")
        queryset = self.get_queryset()

        for campaign in queryset:
            active_comments = campaign.comments.filter(option="Started").select_related(
                "user"
            )
            for comment in active_comments:
                elapsed_time = timezone.now() - comment.created_at
                total_hours = divmod(elapsed_time.total_seconds(), 3600)[
                    0
                ]  # Calculate hours
                reward = total_hours * 5

                user_profile = Profile.objects.get(user=comment.user)
                user_profile.point_achieved = reward
                user_profile.save()
                comment.end_at = timezone.now()
                comment.save()

        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=["get"], url_path="urgent")
    def urgent_campaigns(self, request):
        """Get all urgent campaigns"""
        urgent_campaigns = CampaignModel.objects.filter(urgency_level="Urgent")
        serializer = self.get_serializer(urgent_campaigns, many=True)
        return Response(serializer.data)


# Comment ViewSet
class CommentViewSet(viewsets.ModelViewSet):
    """
    To create volunteer model through comment u need to pass:
    {
        "user":"user_id",
        "option": " Started / Stop",
        "campaign": "campaign_id
    }
    """

    queryset = CommentModel.objects.all().order_by("-created_at")
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
        user_id = request.query_params.get("user_id")
        if user_id:
            user = get_object_or_404(User, user_id=user_id)
            comments = CommentModel.objects.filter(user=user)
        else:
            comments = CommentModel.objects.all()

        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        user_id = request.data.get("user")
        option = request.data.get("option")
        campaign_id = request.data.get("campaign")

        user = get_object_or_404(User, user_id=user_id)
        campaign = get_object_or_404(CampaignModel, id=campaign_id)

        comment, created = CommentModel.objects.get_or_create(
            user=user, campaign=campaign
        )

        if not created:
            if option == "Stop" and comment.option == "Started":
                elapsed_time = timezone.now() - comment.created_at

                total_hours = divmod(elapsed_time.total_seconds(), 3600)[0]
                print("elap", elapsed_time)
                print("thourse", total_hours)
                reward = total_hours * 5

                user.profile.point_achieved += reward
                user.profile.save()

                comment.option = "Stop"
                print(reward)
                comment.total_volunteered += total_hours
                print("total", comment.total_volunteered)
                comment.end_at = timezone.now()
                comment.save()

                return Response(
                    {"message": "Contribution stopped successfully"},
                    status=status.HTTP_200_OK,
                )

            elif option == "Started" and comment.option == "Stop":
                comment.option = "Started"
                comment.end_at = None
                comment.save()

                return Response(
                    {"message": "Contribution restarted successfully"},
                    status=status.HTTP_200_OK,
                )

            return Response(
                {"message": "No changes made"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": "Contribution started successfully", "id": comment.id},
            status=status.HTTP_201_CREATED,
        )


# Event Registration API
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


# Volunteer History API
class VolunteerHistory(generics.ListAPIView):
    serializer_class = HistroySerializer

    def get_queryset(self):
        user = get_object_or_404(User, user_id=self.kwargs["user_id"])
        return CommentModel.objects.filter(user=user)


# Recent User Posts API
class RecentPost(generics.ListAPIView):
    serializer_class = CampaignSerializer

    def get_queryset(self):
        user = get_object_or_404(User, user_id=self.kwargs["user_id"])
        return CampaignModel.objects.filter(creator=user)


def generate_certificate(request, user_id):
    try:
        user = get_object_or_404(User, user_id=user_id)
        if user is None:
            return Response({"message": "User Does not Exist"})
        profile = get_object_or_404(Profile, user=user)
        if profile is None:
            return Response({"message": "User Profile Does not Exist"})
        point = profile.point_achieved
        if point > 19:
            date_generated = datetime.today().strftime("%B %d, %Y")
            response = HttpResponse(content_type="application/pdf")
            response["Content-Disposition"] = (
                f'inline; filename="{profile.full_name}_certificate.pdf"'
            )

            width, height = landscape(A4)
            pdf = canvas.Canvas(response, pagesize=(width, height))

            cert_template_url = "https://i.ibb.co.com/BHSX5rJc/certificate-imag.png"
            pdf.drawImage(cert_template_url, 0, 0, width=width, height=height)
            pdf.setFont("Helvetica-Bold", 30)
            pdf.drawCentredString(
                width / 2, height - 200, "CERTIFICATE OF APPRECIATION"
            )
            pdf.setFont("Helvetica", 14)
            pdf.drawCentredString(width / 2, height - 230, "This is proudly awarded to")

            pdf.setFont("Helvetica-Bold", 30)
            pdf.drawCentredString(width / 2, height - 270, profile.full_name)
            pdf.setFont("Helvetica", 18)
            pdf.drawCentredString(
                width / 2,
                height - 310,
                f"For outstanding volunteering efforts with {profile.point_achieved} points",
            )

            pdf.setFont("Helvetica", 14)
            pdf.drawString(120, 100, f"Date: {date_generated}")

            signature_path = "https://i.ibb.co.com/cX6KTK27/signature.png"
            pdf.drawImage(
                signature_path, width - 300, 50, width=200, height=150, mask="auto"
            )

            pdf.setFont("Helvetica", 12)
            pdf.drawCentredString(width - 200, 100, "Handon's Signature")

            pdf.showPage()
            pdf.save()

            return response
        else:
            return Response({"message": "You need to earn more point."})

    except Exception as e:
        # error,
        error_message = f"An error occurred while generating the certificate: {str(e)}"
        print(error_message)
        return HttpResponse(f"Error: {error_message}", status=500)
