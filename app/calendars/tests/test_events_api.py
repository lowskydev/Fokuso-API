"""
Tests for the Events API.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from datetime import date, time

from core.models import Event


EVENTS_URL = reverse('calendars:event-list-create')
GROUPED_EVENTS_URL = reverse('calendars:events-grouped')
TODAY_EVENTS_URL = reverse('calendars:today-events')


def detail_url(event_id):
    """Return event detail URL"""
    return reverse('calendars:event-detail', args=[event_id])


def create_user(**params):
    """Create and return a sample user"""
    defaults = {
        'email': 'user@example.com',
        'password': 'testpass123',
        'name': 'Test User',
    }
    defaults.update(params)
    return get_user_model().objects.create_user(**defaults)


def create_event(user, **params):
    """Create and return a sample event"""
    defaults = {
        'title': 'Sample Event',
        'description': 'Sample description',
        'date': date.today(),
        'start_time': time(9, 0),
        'end_time': time(10, 0),
        'event_type': 'focus',
    }
    defaults.update(params)
    return Event.objects.create(owner=user, **defaults)


class PublicEventApiTests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test authentication is required for events"""
        res = self.client.get(EVENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateEventApiTests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_events(self):
        """Test retrieving events"""
        create_event(user=self.user)
        create_event(user=self.user, title='Second Event')

        res = self.client.get(EVENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_events_limited_to_user(self):
        """Test events are limited to authenticated user"""
        other_user = create_user(email='other@example.com')
        create_event(user=other_user)
        create_event(user=self.user)

        res = self.client.get(EVENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_create_event(self):
        """Test creating an event"""
        payload = {
            'title': 'New Event',
            'description': 'Event description',
            'date': '2025-06-30',
            'start_time': '14:00',
            'end_time': '15:00',
            'event_type': 'meeting',
        }

        res = self.client.post(EVENTS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        event = Event.objects.get(id=res.data['id'])
        self.assertEqual(event.title, payload['title'])
        self.assertEqual(event.owner, self.user)

    def test_create_event_invalid_time(self):
        """Test creating event with end time before start time fails"""
        payload = {
            'title': 'Invalid Event',
            'date': '2025-06-30',
            'start_time': '15:00',
            'end_time': '14:00',  # End before start
            'event_type': 'focus',
        }

        res = self.client.post(EVENTS_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_events_grouped_by_date(self):
        """Test getting events grouped by date"""
        # Create events on different dates
        create_event(
            user=self.user,
            title='Event 1',
            date=date(2025, 6, 1)
        )
        create_event(
            user=self.user,
            title='Event 2',
            date=date(2025, 6, 1)
        )
        create_event(
            user=self.user,
            title='Event 3',
            date=date(2025, 6, 2)
        )

        res = self.client.get(GROUPED_EVENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('2025-06-01', res.data)
        self.assertIn('2025-06-02', res.data)
        self.assertEqual(len(res.data['2025-06-01']), 2)
        self.assertEqual(len(res.data['2025-06-02']), 1)

    def test_get_today_events(self):
        """Test getting today's events"""
        create_event(user=self.user, date=date.today())
        create_event(user=self.user, date=date(2025, 12, 31))  # Different date

        res = self.client.get(TODAY_EVENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_update_event(self):
        """Test updating an event"""
        event = create_event(user=self.user)

        payload = {
            'title': 'Updated Event',
            'event_type': 'study',
        }

        url = detail_url(event.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        event.refresh_from_db()
        self.assertEqual(event.title, payload['title'])
        self.assertEqual(event.event_type, payload['event_type'])

    def test_delete_event(self):
        """Test deltion of an event"""
        event = create_event(user=self.user)

        url = detail_url(event.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Event.objects.filter(id=event.id).exists())
