"""
Tests for the Todo API.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Todo


TODOS_URL = reverse('todos:todo-list-create')


def detail_url(todo_id):
    """Return todo detail URL"""
    return reverse('todos:todo-detail', args=[todo_id])


def create_user(**params):
    """Create and return a sample user"""
    defaults = {
        'email': 'user@example.com',
        'password': 'testpass123',
        'name': 'Test User',
    }
    defaults.update(params)
    return get_user_model().objects.create_user(**defaults)


def create_todo(user, **params):
    """Create and return a sample todo"""
    defaults = {
        'title': 'Sample Todo',
        'description': 'Sample description',
        'priority': 'medium',
        'category': 'work',
    }
    defaults.update(params)
    return Todo.objects.create(owner=user, **defaults)


class PublicTodoApiTests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test authentication is required for todos"""
        res = self.client.get(TODOS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTodoApiTests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_todos(self):
        """Test retrieving todos"""
        create_todo(user=self.user)
        create_todo(user=self.user, title='Second Todo')

        res = self.client.get(TODOS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_todos_limited_to_user(self):
        """Test todos are limited to authenticated user"""
        other_user = create_user(email='other@example.com')
        create_todo(user=other_user)
        create_todo(user=self.user)

        res = self.client.get(TODOS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_create_todo(self):
        """Test creating a todo"""
        payload = {
            'title': 'New Todo',
            'description': 'Todo description',
            'priority': 'high',
            'category': 'personal',
            'due_date': '2025-12-31',
            'tag_names': ['urgent', 'important']
        }

        res = self.client.post(TODOS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        todo = Todo.objects.get(id=res.data['id'])
        self.assertEqual(todo.title, payload['title'])
        self.assertEqual(todo.owner, self.user)
        self.assertEqual(todo.tags.count(), 2)

    def test_create_todo_with_tags(self):
        """Test creating todo with tags"""
        payload = {
            'title': 'Tagged Todo',
            'tag_names': ['work', 'urgent', 'meeting']
        }

        res = self.client.post(TODOS_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        todo = Todo.objects.get(id=res.data['id'])
        self.assertEqual(todo.tags.count(), 3)
        tag_names = [tag.name for tag in todo.tags.all()]
        self.assertIn('work', tag_names)
        self.assertIn('urgent', tag_names)
        self.assertIn('meeting', tag_names)

    def test_update_todo(self):
        """Test updating a todo"""
        todo = create_todo(user=self.user)

        payload = {
            'title': 'Updated Todo',
            'completed': True,
            'tag_names': ['completed', 'done']
        }

        url = detail_url(todo.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        todo.refresh_from_db()
        self.assertEqual(todo.title, payload['title'])
        self.assertTrue(todo.completed)

    def test_delete_todo(self):
        """Test deleting a todo"""
        todo = create_todo(user=self.user)

        url = detail_url(todo.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Todo.objects.filter(id=todo.id).exists())

    def test_filter_todos_by_completed(self):
        """Test filtering todos by completion status"""
        create_todo(user=self.user, title='Completed', completed=True)
        create_todo(user=self.user, title='Not completed', completed=False)

        res = self.client.get(TODOS_URL, {'completed': 'true'})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['title'], 'Completed')

    def test_filter_todos_by_priority(self):
        """Test filtering todos by priority"""
        create_todo(user=self.user, title='High Priority', priority='high')
        create_todo(user=self.user, title='Low Priority', priority='low')

        res = self.client.get(TODOS_URL, {'priority': 'high'})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['title'], 'High Priority')
