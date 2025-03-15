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
    email = models.EmailField(unique=True, db_index=True)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    otp = models.CharField(
        unique=True, max_length=20, null=True, blank=True, db_index=True
    )
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

    def Profile(self):
        return Profile.objects.filter(user=self).first()

    def user_skills(self):
        return ProfileSkills.objects.filter(profile=self.profile)

    def user_interest(self):
        return ProfileCauses.objects.filter(profile__user=self)


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
    # For Fast lookups we are using user one to one as primary
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile", primary_key=True
    )
    full_name = models.CharField(max_length=100, blank=True, null=True)
    image = models.URLField(
        default="https://res.cloudinary.com/dofqxmuya/image/upload/v1739757761/qx57adbbmy6vkh577y3j.png",
        null=True,
        blank=True,
    )
    info = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    point_achieved = models.IntegerField(default=0, null=True)

    def __str__(self):
        if self.full_name:
            return f"{self.full_name}"
        else:
            return f"{self.user.full_name}"

    def save(self, *args, **kwargs):
        if self.full_name == "" or self.full_name is None:
            self.full_name = self.user.full_name
        super(Profile, self).save(*args, **kwargs)


class ProfileSkills(models.Model):  # 👈 Custom Many-to-Many Table
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="skills", db_index=True
    )
    skill = models.ForeignKey(SkillsModel, on_delete=models.CASCADE)

    def __str__(self):
        return self.profile.user.username

    class Meta:
        unique_together = ("profile", "skill")


class ProfileCauses(models.Model):  # 👈 Custom Many-to-Many Table
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="causes", db_index=True
    )
    cause = models.ForeignKey(CausesChoicesModel, on_delete=models.CASCADE)

    def __str__(self):
        return self.profile.user.username

    class Meta:
        unique_together = ("profile", "cause")
