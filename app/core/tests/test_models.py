"""
Test for models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models

from django.utils import timezone
from datetime import timedelta


def create_user(email='user@example.com', password='testpass123'):
    """Helper function to create a user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    """Test models"""

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test creating user without email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_flashcard(self):
        """Test creating a flashcard is successful"""
        user = create_user()
        # Create a deck first since flashcard requires one
        deck = models.Deck.objects.create(
            owner=user,
            name='Test Deck'
        )
        flashcard = models.Flashcard.objects.create(
            owner=user,
            deck=deck,  # Add the required deck
            question='What is the capital of France?',
            answer='Paris',
            next_review=timezone.now() + timedelta(days=1),
        )

        self.assertEqual(flashcard.owner, user)
        self.assertEqual(flashcard.deck, deck)
        self.assertEqual(flashcard.question, 'What is the capital of France?')
        self.assertEqual(flashcard.answer, 'Paris')
