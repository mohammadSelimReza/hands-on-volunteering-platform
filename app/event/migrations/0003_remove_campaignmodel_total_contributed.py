# Generated by Django 5.1.7 on 2025-03-16 19:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0002_commentmodel_end_at_alter_campaignmodel_created_at_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='campaignmodel',
            name='total_contributed',
        ),
    ]
