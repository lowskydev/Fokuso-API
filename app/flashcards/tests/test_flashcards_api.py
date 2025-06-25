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

from core.models import Flashcard, Deck

from flashcards.serializers import FlashcardSerializer, FlashcardListSerializer


FLASHCARDS_URL = reverse('flashcards:flashcard-list-create')


def detail_url(flashcard_id):
    """Return flashcard detail URL."""
    return reverse('flashcards:flashcard-detail', args=[flashcard_id])


def create_user(**params):
    """Create and return a sample user."""
    return get_user_model().objects.create_user(**params)


def create_deck(user, **params):
    """Create and return a sample deck."""
    defaults = {'name': 'Test Deck'}
    defaults.update(params)

    # Try to get existing deck first, create if it doesn't exist
    try:
        return Deck.objects.get(owner=user, name=defaults['name'])
    except Deck.DoesNotExist:
        return Deck.objects.create(owner=user, **defaults)


def create_flashcard(user, **params):
    """Create and return a sample flashcard."""
    # Create a deck if not provided
    if 'deck' not in params:
        params['deck'] = create_deck(user)

    defaults = {
        'question': 'Sample question?',
        'answer': 'Sample answer.',
        'next_review': '2025-05-26T14:06:31.079Z',
        'interval': 1,
        'ease_factor': 250,  # Changed to integer
        'repetition': 0,
    }
    defaults.update(params)

    flashcard = Flashcard.objects.create(owner=user, **defaults)
    return flashcard


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
        # Create a shared deck for all tests in this class
        self.deck = create_deck(user=self.user, name='Shared Test Deck')

    def test_retrieve_flashcards(self):
        """Test retrieving a list of flashcards."""
        create_flashcard(user=self.user, deck=self.deck)
        create_flashcard(user=self.user, deck=self.deck)

        response = self.client.get(FLASHCARDS_URL)

        flashcards = Flashcard.objects.all().order_by('created_at')
        serializer = FlashcardListSerializer(flashcards, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_flashcards_limited_to_user(self):
        """Test retrieving flashcards for the authenticated user."""
        other_user = create_user(
            email='other@example.com',
            password='testpass123'
        )
        other_deck = create_deck(user=other_user, name='Other User Deck')

        create_flashcard(user=other_user, deck=other_deck)
        create_flashcard(user=self.user, deck=self.deck)

        response = self.client.get(FLASHCARDS_URL)

        flashcards = Flashcard.objects.filter(
            owner=self.user
            ).order_by('-created_at')
        serializer = FlashcardListSerializer(flashcards, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_flashcard_detail(self):
        """Test retrieving a flashcard detail."""
        flashcard = create_flashcard(user=self.user, deck=self.deck)

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
            'deck': self.deck.id,  # Use the shared deck
        }

        response = self.client.post(FLASHCARDS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        flashcard = Flashcard.objects.get(id=response.data['id'])
        self.assertEqual(flashcard.question, payload['question'])
        self.assertEqual(flashcard.answer, payload['answer'])
        self.assertEqual(flashcard.deck.id, payload['deck'])
        self.assertEqual(flashcard.owner, self.user)

    def test_partial_update_flashcard(self):
        """Test partially updating a flashcard."""
        flashcard = create_flashcard(user=self.user, deck=self.deck)

        payload = {'question': 'Updated question?'}
        url = detail_url(flashcard.id)
        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        flashcard.refresh_from_db()
        self.assertEqual(flashcard.question, payload['question'])

    def test_full_update_flashcard(self):
        """Test fully updating a flashcard."""
        flashcard = create_flashcard(user=self.user, deck=self.deck)

        payload = {
            'question': 'New question?',
            'answer': 'New answer.',
            'deck': self.deck.id,
        }

        url = detail_url(flashcard.id)
        response = self.client.put(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        flashcard.refresh_from_db()
        self.assertEqual(flashcard.question, payload['question'])
        self.assertEqual(flashcard.answer, payload['answer'])
        self.assertEqual(flashcard.deck.id, payload['deck'])
        self.assertEqual(flashcard.owner, self.user)

    def test_delete_flashcard(self):
        """Test deleting a flashcard."""
        flashcard = create_flashcard(user=self.user, deck=self.deck)

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
        other_deck = create_deck(user=other_user, name='Other User Deck 2')
        flashcard = create_flashcard(user=other_user, deck=other_deck)

        url = detail_url(flashcard.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Flashcard.objects.filter(id=flashcard.id).exists())
