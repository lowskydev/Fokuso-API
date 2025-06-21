"""
Database models
"""
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

from django.conf import settings

from decimal import Decimal

from django.utils import timezone


class UserManager(BaseUserManager):
    """Manager for users"""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user"""
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


# AbstractBaseUser - functionality for auth system
# PermissionsMixin - adds permission fields to user model
class User(AbstractBaseUser, PermissionsMixin):
    """User in the system"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Note(models.Model):
    """Note object"""
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notes'
    )
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.title


class Deck(models.Model):
    """Deck object for organizing flashcards"""
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='decks',
    )
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('owner', 'name')
        ordering = ['-updated_at']

    def __str__(self):
        return self.name


class Flashcard(models.Model):
    """Flashcard object"""
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='flashcards'
    )
    deck = models.ForeignKey(
        Deck,
        on_delete=models.CASCADE,
        related_name='flashcards',
        blank=False,  # Changed from True
        null=False    # Changed from True
    )
    question = models.TextField(blank=False)
    answer = models.TextField(blank=False)
    # The next review date for the flashcard - set to now by default
    next_review = models.DateTimeField(default=timezone.now)
    interval = models.IntegerField(default=1)  # in minutes
    # Ease factor for spaced repetition (stored as percentage, e.g., 250 = 2.5x)
    ease_factor = models.IntegerField(default=250)
    repetition = models.IntegerField(default=0)
    is_learning = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-next_review']

    def __str__(self):
        return f"Flashcard {self.id} - {self.question[:50]}..."

    @property
    def interval_display(self):
        """Return a human-readable interval"""
        if self.interval < 60:
            return f"{self.interval} minute{'s' if self.interval != 1 else ''}"
        elif self.interval < 1440:
            hours = self.interval // 60
            return f"{hours} hour{'s' if hours != 1 else ''}"
        else:
            days = self.interval // 1440
            return f"{days} day{'s' if days != 1 else ''}"


class DailyReviewStats(models.Model):
    """Daily review statistics for users"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='daily_review_stats'
    )
    date = models.DateField()
    flashcards_reviewed = models.IntegerField(default=0)
    correct_reviews = models.IntegerField(default=0)
    incorrect_reviews = models.IntegerField(default=0)
    total_review_time_minutes = models.IntegerField(default=0)  # Optional: track time spent
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.email} - {self.date} - {self.flashcards_reviewed} reviews"

    @property
    def accuracy_percentage(self):
        """Calculate accuracy percentage"""
        if self.flashcards_reviewed == 0:
            return 0
        return round((self.correct_reviews / self.flashcards_reviewed) * 100, 1)


class ReviewLog(models.Model):
    """Log of flashcard reviews"""
    flashcard = models.ForeignKey(
        Flashcard,
        on_delete=models.CASCADE,
        related_name='review_logs'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='review_logs'
    )
    reviewed_at = models.DateTimeField(auto_now_add=True)
    grade = models.IntegerField()  # Recall grade (0-5)

    class Meta:
        ordering = ['-reviewed_at']

    def __str__(self):
        return (f"Review {self.id} for Flashcard {self.flashcard.id}" +
                f" by {self.user.email} at {self.reviewed_at}" +
                f" - Grade: {self.grade}")
