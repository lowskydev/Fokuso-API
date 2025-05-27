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
        blank=True,
        null=True
    )
    question = models.TextField(blank=False)
    answer = models.TextField(blank=False)
    # The next review date for the flashcard
    next_review = models.DateTimeField(default=timezone.now)
    interval = models.IntegerField(default=1)  # in days
    # Ease factor for spaced repetition SM2 algorithm
    ease_factor = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('2.50')
    )
    repetition = models.IntegerField(default=0)  # number of repetitions
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-next_review']

    def __str__(self):
        return f"Flashcard {self.id} - {self.question[:50]}..."
