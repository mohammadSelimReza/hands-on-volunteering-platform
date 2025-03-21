from django.contrib import admin

from .models import (
    CausesChoicesModel,
    Profile,
    ProfileCauses,
    ProfileSkills,
    SkillsModel,
    User,
)


# Register your models here.
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "full_name", "created_at"]


admin.site.register(User)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(SkillsModel)
admin.site.register(CausesChoicesModel)
admin.site.register(ProfileSkills)
admin.site.register(ProfileCauses)
