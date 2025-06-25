"""
Tests for the Tag API.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag


TAGS_URL = reverse('todos:tag-list-create')


def detail_url(tag_id):
    """Return tag detail URL"""
    return reverse('todos:tag-detail', args=[tag_id])


def create_user(**params):
    """Create and return a sample user"""
    defaults = {
        'email': 'user@example.com',
        'password': 'testpass123',
        'name': 'Test User',
    }
    defaults.update(params)
    return get_user_model().objects.create_user(**defaults)


def create_tag(user, **params):
    """Create and return a sample tag"""
    defaults = {'name': 'sample-tag'}
    defaults.update(params)
    return Tag.objects.create(owner=user, **defaults)


class PublicTagApiTests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test authentication is required for tags"""
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagApiTests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags"""
        create_tag(user=self.user, name='work')
        create_tag(user=self.user, name='personal')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_tags_limited_to_user(self):
        """Test tags are limited to authenticated user"""
        other_user = create_user(email='other@example.com')
        create_tag(user=other_user, name='other-tag')
        create_tag(user=self.user, name='my-tag')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], 'my-tag')

    def test_create_tag(self):
        """Test creating a tag"""
        payload = {'name': 'urgent'}

        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        tag = Tag.objects.get(id=res.data['id'])
        self.assertEqual(tag.name, payload['name'])
        self.assertEqual(tag.owner, self.user)

    def test_create_duplicate_tag_fails(self):
        """Test creating duplicate tag fails"""
        create_tag(user=self.user, name='work')
        payload = {'name': 'work'}

        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
