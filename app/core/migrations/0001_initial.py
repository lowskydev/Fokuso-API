# Generated by Django 3.2.25 on 2025-06-21 14:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Deck',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='decks', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-updated_at'],
                'unique_together': {('owner', 'name')},
            },
        ),
        migrations.CreateModel(
            name='Flashcard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField()),
                ('answer', models.TextField()),
                ('next_review', models.DateTimeField(default=django.utils.timezone.now)),
                ('interval', models.IntegerField(default=1)),
                ('ease_factor', models.IntegerField(default=250)),
                ('repetition', models.IntegerField(default=0)),
                ('is_learning', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deck', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='flashcards', to='core.deck')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='flashcards', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-next_review'],
            },
        ),
        migrations.CreateModel(
            name='ReviewLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reviewed_at', models.DateTimeField(auto_now_add=True)),
                ('grade', models.IntegerField()),
                ('flashcard', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='review_logs', to='core.flashcard')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='review_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-reviewed_at'],
            },
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='DailyReviewStats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('flashcards_reviewed', models.IntegerField(default=0)),
                ('correct_reviews', models.IntegerField(default=0)),
                ('incorrect_reviews', models.IntegerField(default=0)),
                ('total_review_time_minutes', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_review_stats', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date'],
                'unique_together': {('user', 'date')},
            },
        ),
    ]
