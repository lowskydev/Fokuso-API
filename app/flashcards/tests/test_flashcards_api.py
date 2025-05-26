"""
Tests for the Flashcards API endpoints.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from django.utils.dateparse import parse_datetime

from core.models import Flashcard

from flashcards.serializers import FlashcardSerializer


FLASHCARDS_URL = reverse('flashcards:flashcard-list-create')


def detail_url(flashcard_id):
    """Return flashcard detail URL."""
    return reverse('flashcards:flashcard-detail', args=[flashcard_id])


def create_flashcard(user, **params):
    """Create and return a sample flashcard."""
    defaults = {
        'question': 'Sample question?',
        'answer': 'Sample answer.',
        'next_review': '2025-05-26T14:06:31.079Z',
        'interval': 1,
        'ease_factor': Decimal('2.30'),
        'repetition': 0,
    }
    defaults.update(params)

    flashcard = Flashcard.objects.create(owner=user, **defaults)
    return flashcard


def create_user(**params):
    """Create and return a sample user."""
    return get_user_model().objects.create_user(**params)


class PublicFlashcardsApiTests(TestCase):
    """Test the public features of the Flashcards API."""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access flashcards."""
        response = self.client.get(FLASHCARDS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateFlashcardsApiTests(TestCase):
    """Test the private features of the Flashcards API."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='user@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_flashcards(self):
        """Test retrieving a list of flashcards."""
        create_flashcard(user=self.user)
        create_flashcard(user=self.user)

        response = self.client.get(FLASHCARDS_URL)

        flashcards = Flashcard.objects.all().order_by('created_at')
        serializer = FlashcardSerializer(flashcards, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_flashcards_limited_to_user(self):
        """Test retrieving flashcards for the authenticated user."""
        other_user = create_user(
            email='other@example.com',
            password='testpass123'
        )

        create_flashcard(user=other_user)
        create_flashcard(user=self.user)

        response = self.client.get(FLASHCARDS_URL)

        flashcards = Flashcard.objects.filter(
            owner=self.user
            ).order_by('-created_at')
        serializer = FlashcardSerializer(flashcards, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_flashcard_detail(self):
        """Test retrieving a flashcard detail."""
        flashcard = create_flashcard(user=self.user)

        url = detail_url(flashcard.id)
        response = self.client.get(url)

        serializer = FlashcardSerializer(flashcard)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for key in serializer.data:
            if key == 'ease_factor':
                self.assertEqual(
                    Decimal(response.data[key]),
                    Decimal(serializer.data[key])
                )
            elif key == 'next_review':
                self.assertEqual(
                    parse_datetime(response.data[key]),
                    parse_datetime(serializer.data[key])
                )
            else:
                self.assertEqual(response.data[key], serializer.data[key])

    def test_create_flashcard(self):
        """Test creating a flashcard."""
        payload = {
            'question': 'What is the capital of France?',
            'answer': 'Paris',
            'next_review': '2025-05-26T14:06:31.079Z',
            'interval': 1,
            'ease_factor': Decimal('2.5'),
            'repetition': 0,
        }

        # Ensure the next_review is in the correct format
        payload['next_review'] = parse_datetime(payload['next_review'])

        response = self.client.post(FLASHCARDS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        flashcard = Flashcard.objects.get(id=response.data['id'])
        for key in payload:
            self.assertEqual(getattr(flashcard, key), payload[key])

        self.assertEqual(flashcard.owner, self.user)

    def test_partial_update_flashcard(self):
        """Test partially updating a flashcard."""
        flashcard = create_flashcard(user=self.user)

        payload = {'question': 'Updated question?'}
        url = detail_url(flashcard.id)
        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        flashcard.refresh_from_db()
        self.assertEqual(flashcard.question, payload['question'])

    def test_full_update_flashcard(self):
        """Test fully updating a flashcard."""
        flashcard = create_flashcard(user=self.user)

        payload = {
            'question': 'New question?',
            'answer': 'New answer.',
            'next_review': '2025-05-26T14:06:31.079Z',
            'interval': 2,
            'ease_factor': Decimal('3.0'),
            'repetition': 1,
        }

        # Ensure the next_review is in the correct format
        payload['next_review'] = parse_datetime(payload['next_review'])

        url = detail_url(flashcard.id)
        response = self.client.put(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        flashcard.refresh_from_db()
        for key in payload:
            self.assertEqual(getattr(flashcard, key), payload[key])

        self.assertEqual(flashcard.owner, self.user)

    def test_delete_flashcard(self):
        """Test deleting a flashcard."""
        flashcard = create_flashcard(user=self.user)

        url = detail_url(flashcard.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Flashcard.objects.filter(id=flashcard.id).exists())

    def test_delete_other_user_flashcard_returns_error(self):
        """Test trying to delete another user's flashcard returns an error."""
        other_user = create_user(
            email='user2@example.com',
            password='testpass123'
        )
        flashcard = create_flashcard(user=other_user)

        url = detail_url(flashcard.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Flashcard.objects.filter(id=flashcard.id).exists())
