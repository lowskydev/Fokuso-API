"""
Tests for the Deck API.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Deck
from flashcards.serializers import DeckSerializer


DECKS_URL = reverse('flashcards:deck-list-create')


def detail_url(deck_id):
    """Return deck detail URL."""
    return reverse('flashcards:deck-detail', args=[deck_id])


def create_deck(user, **params):
    """Create and return a sample deck."""
    defaults = {'name': 'Sample Deck'}
    defaults.update(params)
    return Deck.objects.create(owner=user, **defaults)


def create_user(**params):
    """Create and return a sample user."""
    return get_user_model().objects.create_user(**params)


class PublicDeckApiTests(TestCase):
    """Test the public features of the Deck API."""
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that authentication is required to access decks."""
        response = self.client.get(DECKS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateDeckApiTests(TestCase):
    """Test the private features of the Deck API."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='user@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_decks(self):
        """Test retrieving a list of decks."""
        create_deck(user=self.user)
        create_deck(user=self.user, name="Second Deck")

        response = self.client.get(DECKS_URL)

        decks = Deck.objects.filter(owner=self.user).order_by('updated_at')
        serializer = DeckSerializer(decks, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_decks_limited_to_user(self):
        """Test that only user's decks are returned."""
        other_user = create_user(
            email='other@example.com',
            password='testpass123'
        )
        create_deck(user=other_user)
        deck = create_deck(user=self.user)

        response = self.client.get(DECKS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], deck.id)

    def test_create_deck(self):
        """Test creating a deck."""
        payload = {'name': 'History Deck'}

        response = self.client.post(DECKS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        deck = Deck.objects.get(id=response.data['id'])
        self.assertEqual(deck.name, payload['name'])
        self.assertEqual(deck.owner, self.user)

    def test_get_deck_detail(self):
        """Test retrieving a deck detail."""
        deck = create_deck(user=self.user)

        url = detail_url(deck.id)
        response = self.client.get(url)

        serializer = DeckSerializer(deck)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_update_deck(self):
        """Test updating a deck."""
        deck = create_deck(user=self.user)

        payload = {'name': 'Updated Deck Name'}
        url = detail_url(deck.id)
        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        deck.refresh_from_db()
        self.assertEqual(deck.name, payload['name'])

    def test_delete_deck(self):
        """Test deleting a deck."""
        deck = create_deck(user=self.user)

        url = detail_url(deck.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Deck.objects.filter(id=deck.id).exists())

    def test_delete_other_users_deck_returns_error(self):
        """Test that you cannot delete another user's deck."""
        other_user = create_user(
            email='user2@example.com',
            password='testpass123'
        )
        deck = create_deck(user=other_user)

        url = detail_url(deck.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Deck.objects.filter(id=deck.id).exists())
