# Generated by Django 5.1.7 on 2025-03-18 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commentmodel',
            name='total_volunteered',
            field=models.PositiveIntegerField(default=0, null=True),
        ),
    ]
