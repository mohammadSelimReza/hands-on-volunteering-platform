# Generated by Django 5.1.7 on 2025-03-13 07:01

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('event', '0001_initial'),
        ('user', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='eventmodel',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='eventsCategory', to='user.causeschoicesmodel'),
        ),
        migrations.AddField(
            model_name='eventmodel',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='event_created', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='eventmodel',
            name='skills_required',
            field=models.ManyToManyField(to='user.skillsmodel'),
        ),
        migrations.AddField(
            model_name='eventmodel',
            name='location',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='eventsArea', to='event.locationmodel'),
        ),
        migrations.AddField(
            model_name='registerpeople',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registered_people', to='event.eventmodel'),
        ),
        migrations.AddField(
            model_name='registerpeople',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
