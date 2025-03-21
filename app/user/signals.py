from django.db.models.signals import post_save

from .models import Profile, User


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        profile = instance.profile
        if profile.full_name != instance.full_name:
            profile.full_name = instance.full_name
            profile.save()


def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)
