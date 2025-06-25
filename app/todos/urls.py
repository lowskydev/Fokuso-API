"""
URLs for the todos app.
"""
from django.urls import path
from todos.views import (
    TodoListCreateView,
    TodoDetailView,
    TagListCreateView,
    TagDetailView,
)

app_name = 'todos'

urlpatterns = [
    # Todo endpoints
    path('', TodoListCreateView.as_view(), name='todo-list-create'),
    path('<int:pk>/', TodoDetailView.as_view(), name='todo-detail'),

    # Tag endpoints
    path('tags/', TagListCreateView.as_view(), name='tag-list-create'),
    path('tags/<int:pk>/', TagDetailView.as_view(), name='tag-detail'),
]
