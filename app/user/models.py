from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify
from shortuuid.django_fields import ShortUUIDField

# Create your models here.


class User(AbstractUser):
    # user information:
    user_id = ShortUUIDField(
        length=6, max_length=6, alphabet="0123456789", primary_key=True
    )
    username = models.CharField(max_length=30, unique=True, db_index=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    otp = models.CharField(unique=True, max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        email_user, _ = self.email.split("@")
        if self.username == "" or self.username is None:
            self.username = email_user
        if self.full_name == "" or self.full_name is None:
            self.full_name = f"{self.first_name} {self.last_name}"
        super(User, self).save(*args, **kwargs)


class SkillsModel(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class CausesChoicesModel(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug is None:
            self.slug = slugify(self.name)
        super(CausesChoicesModel, self).save(*args, **kwargs)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=100, blank=True, null=True)
    image = models.URLField(
        default="https://res.cloudinary.com/dofqxmuya/image/upload/v1739757761/qx57adbbmy6vkh577y3j.png",
        null=True,
        blank=True,
    )
    info = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    skills = models.ManyToManyField(SkillsModel, blank=True)
    causeschoices = models.ManyToManyField(CausesChoicesModel, blank=True)

    def __str__(self):
        if self.full_name:
            return f"{self.full_name}"
        else:
            return f"{self.user.full_name}"

    def save(self, *args, **kwargs):
        if self.full_name == "" or self.full_name is None:
            self.full_name = self.user.full_name
        super(Profile, self).save(*args, **kwargs)
