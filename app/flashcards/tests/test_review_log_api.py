"""
Tests for the Review Log API.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Flashcard, Deck, ReviewLog
from django.utils import timezone


REVIEW_LOGS_URL = reverse('flashcards:review-log-list')


def create_user(**params):
    """Create and return a sample user."""
    return get_user_model().objects.create_user(**params)


def create_deck(user, name="Test Deck"):
    """Create and return a sample deck."""
    return Deck.objects.create(owner=user, name=name)


def create_flashcard(user, deck, **params):
    """Create and return a sample flashcard."""
    defaults = {
        'question': 'Sample question?',
        'answer': 'Sample answer.',
        'deck': deck,
        'next_review': timezone.now(),
        'interval': 1,
        'ease_factor': 250,  # Changed to integer
        'repetition': 0,
    }
    defaults.update(params)
    return Flashcard.objects.create(owner=user, **defaults)


def review_url(flashcard_id):
    """Create and return the review URL for a flashcard."""
    return reverse('flashcards:flashcard-review', args=[flashcard_id])


class PublicReviewLogApiTests(TestCase):
    """Test the public features of the Review Log API."""
    def setUp(self):
        """Set up the API client for public tests."""
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required to access review logs."""
        res = self.client.get(REVIEW_LOGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateReviewLogApiTests(TestCase):
    """Test the private features of the Review Log API."""
    def setUp(self):
        """Set up the API client and create a user, deck, and flashcard."""
        self.client = APIClient()
        self.user = create_user(
            email='user@example.com',
            password='testpass123',
        )
        self.client.force_authenticate(self.user)
        self.deck = create_deck(self.user)
        self.flashcard = create_flashcard(self.user, deck=self.deck)

    def test_review_log_created_on_review(self):
        """Test a ReviewLog is created when reviewing a flashcard."""
        payload = {'grade': 2}  # Changed from 4 to 2 (valid range is 1-3)
        res = self.client.post(review_url(self.flashcard.id),
                               payload,
                               format='json',
                               )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        logs = ReviewLog.objects.filter(
            user=self.user,
            flashcard=self.flashcard,
        )
        self.assertEqual(logs.count(), 1)
        log = logs.first()
        self.assertEqual(log.grade, 2)
        self.assertIsNotNone(log.reviewed_at)

    def test_review_log_list(self):
        """Test listing review logs for the authenticated user."""
        # Create a couple of review logs
        ReviewLog.objects.create(
            user=self.user,
            flashcard=self.flashcard,
            grade=2,
        )
        ReviewLog.objects.create(
            user=self.user,
            flashcard=self.flashcard,
            grade=3,
        )

        res = self.client.get(REVIEW_LOGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertTrue(all(
            log['flashcard_id'] == self.flashcard.id for log in res.data
        ))

    def test_review_log_limited_to_user(self):
        """Test that a user only sees their own review logs."""
        other_user = create_user(
            email='other@example.com',
            password='testpass123',
        )
        other_deck = create_deck(other_user)
        other_flashcard = create_flashcard(other_user, deck=other_deck)
        ReviewLog.objects.create(
            user=other_user,
            flashcard=other_flashcard,
            grade=3,
        )
        ReviewLog.objects.create(
            user=self.user,
            flashcard=self.flashcard,
            grade=2,
        )

        res = self.client.get(REVIEW_LOGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['grade'], 2)
