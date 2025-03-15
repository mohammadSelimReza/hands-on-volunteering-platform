from django.contrib import admin

from .models import (
    CampaignModel,
    CommentModel,
    EventModel,
    LocationModel,
    RegisterPeople,
)

# Register your models here.
admin.site.register(LocationModel)
admin.site.register(EventModel)
admin.site.register(RegisterPeople)
admin.site.register(CampaignModel)
admin.site.register(CommentModel)
