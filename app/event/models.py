import math
import uuid

from django.db import models
from django.utils import timezone
from shortuuid.django_fields import ShortUUIDField

from app.user import models as user_model


# Create your models here.
class LocationModel(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class EventModel(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    created_by = models.ForeignKey(
        user_model.User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="event_created",
    )
    image = models.URLField(null=True)
    description = models.CharField(max_length=200)
    location = models.OneToOneField(
        LocationModel, on_delete=models.SET_NULL, null=True, db_index=True
    )
    category = models.ForeignKey(
        user_model.CausesChoicesModel,
        on_delete=models.SET_NULL,
        null=True,
        related_name="eventsCategory",
        db_index=True,
    )
    skills_required = models.ManyToManyField(user_model.SkillsModel)
    private = models.BooleanField(default=False)
    event_id = models.UUIDField(
        default=uuid.uuid4, unique=True, primary_key=True, editable=False, db_index=True
    )
    event_start = models.DateTimeField(db_index=True)
    event_end = models.DateTimeField(db_index=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def is_available(self):
        return self.event_end >= timezone.now()

    def registered_people(self):
        return RegisterPeople.objects.filter(event=self)


class RegisterPeople(models.Model):
    event = models.ForeignKey(
        EventModel, on_delete=models.CASCADE, related_name="registered_people"
    )
    user = models.ForeignKey(
        user_model.User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    registered_status = models.BooleanField(default=False)
    registed_id = ShortUUIDField(
        length=15,
        max_length=30,
        alphabet="abcdefghijklmnopqrstuvwxyz0123456789",
        primary_key=True,
    )
    registered_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.full_name} registered for {self.event.title} on {self.registed_id} "


# Campaing:
class CampaignModel(models.Model):
    URGENCY_LEVELS = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("Urgent", "Urgent"),
    ]

    creator = models.ForeignKey(
        user_model.User, on_delete=models.CASCADE, related_name="campaigns"
    )
    title = models.CharField(max_length=255)
    body = models.TextField()
    image = models.URLField(null=True, blank=True)
    urgency_level = models.CharField(
        max_length=10, choices=URGENCY_LEVELS, default="Low", db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.urgency_level}"

    def total_comments(self):
        return self.comments.count()

    def total_time_from_start(self):
        elapsed_time = timezone.now() - self.created_at
        return math.floor(elapsed_time.total_seconds() / 3600)

    def total_volunteered_time(self):
        contributes = CommentModel.objects.filter(campaign=self)
        return sum(contribute.total_time() for contribute in contributes)


class CommentModel(models.Model):
    status = (("Started", "Started"), ("Stop", "Stop"))
    campaign = models.ForeignKey(
        CampaignModel, on_delete=models.CASCADE, related_name="comments"
    )
    user = models.ForeignKey(user_model.User, on_delete=models.SET_NULL, null=True)
    option = models.TextField(max_length=20, choices=status)
    created_at = models.DateTimeField()
    end_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Contributed by {self.user.full_name}"

    def total_time(self):
        if self.end_at is not None and self.option == "Stop":
            elapsed_time = self.end_at - self.created_at
        else:
            elapsed_time = timezone.now() - self.created_at
        return math.floor(elapsed_time.total_seconds() / 3600)
