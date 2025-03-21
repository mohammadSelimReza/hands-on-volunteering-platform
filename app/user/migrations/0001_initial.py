# Generated by Django 5.1.7 on 2025-03-18 23:42

import django.contrib.auth.models
import django.db.models.deletion
import django.utils.timezone
import shortuuid.django_fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('user_id', shortuuid.django_fields.ShortUUIDField(alphabet='0123456789', length=6, max_length=6, prefix='', primary_key=True, serialize=False)),
                ('username', models.CharField(db_index=True, max_length=30, unique=True)),
                ('first_name', models.CharField(blank=True, max_length=50, null=True)),
                ('last_name', models.CharField(blank=True, max_length=50, null=True)),
                ('email', models.EmailField(db_index=True, max_length=254, unique=True)),
                ('full_name', models.CharField(blank=True, max_length=100, null=True)),
                ('otp', models.CharField(blank=True, db_index=True, max_length=20, null=True, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='CausesChoicesModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('slug', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SkillsModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='profile', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('full_name', models.CharField(blank=True, max_length=100, null=True)),
                ('image', models.URLField(blank=True, default='https://res.cloudinary.com/dofqxmuya/image/upload/v1739757761/qx57adbbmy6vkh577y3j.png', null=True)),
                ('info', models.TextField(blank=True, null=True)),
                ('city', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('volunteer_status', models.BooleanField(default=False)),
                ('point_achieved', models.IntegerField(default=0, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProfileSkills',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('skill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.skillsmodel')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='skills', to='user.profile')),
            ],
            options={
                'unique_together': {('profile', 'skill')},
            },
        ),
        migrations.CreateModel(
            name='ProfileCauses',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cause', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.causeschoicesmodel')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='causes', to='user.profile')),
            ],
            options={
                'unique_together': {('profile', 'cause')},
            },
        ),
    ]
