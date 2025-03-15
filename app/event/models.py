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
    event_end = models.DateTimeField(db_index=True)
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
    target = models.CharField(
        max_length=255, help_text="What is needed? (e.g., 'Winter Clothes')"
    )
    urgency_level = models.CharField(
        max_length=10, choices=URGENCY_LEVELS, default="medium"
    )
    total_target = models.PositiveIntegerField(
        help_text="Total number of items/help needed"
    )
    collected = models.PositiveIntegerField(
        default=0, help_text="Current progress of collected contributions"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.urgency_level}"

    def collection_remaining(self):
        return self.total_target - self.collected

    def progress_percentage(self):
        """Returns the percentage of the goal achieved."""
        return (
            round((self.collected / self.total_target) * 100, 2)
            if self.total_target
            else 0
        )

    def comment_list(self):
        return CommentModel.objects.filter(campaign=self).count()


class CommentModel(models.Model):
    campaign = models.ForeignKey(
        CampaignModel, on_delete=models.CASCADE, related_name="comments"
    )
    user = models.ForeignKey(user_model.User, on_delete=models.SET_NULL, null=True)
    text = models.TextField()
    collected = models.PositiveIntegerField(
        default=0, help_text="Current progress of collected contributions"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username if self.user else 'Anonymous'} on {self.campaign.title}"
