# Generated by Django 5.1.7 on 2025-03-16 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0008_alter_campaignmodel_urgency_level'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='campaignmodel',
            name='collected',
        ),
        migrations.RemoveField(
            model_name='campaignmodel',
            name='target',
        ),
        migrations.RemoveField(
            model_name='campaignmodel',
            name='total_target',
        ),
        migrations.RemoveField(
            model_name='campaignmodel',
            name='updated_at',
        ),
        migrations.RemoveField(
            model_name='commentmodel',
            name='collected',
        ),
        migrations.RemoveField(
            model_name='commentmodel',
            name='text',
        ),
        migrations.AddField(
            model_name='campaignmodel',
            name='total_contributed',
            field=models.PositiveIntegerField(default=1, help_text='Total number of items/help needed'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='commentmodel',
            name='end_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='commentmodel',
            name='option',
            field=models.TextField(choices=[('Started', 'Started'), ('Stop', 'Stop')], default=1, max_length=20),
            preserve_default=False,
        ),
    ]
