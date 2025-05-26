from django.urls import path
from .views import NoteListCreateView, NoteDetailView

urlpatterns = [
    path('', NoteListCreateView.as_view(), name='note-list-create'),
    path('<int:pk>/', NoteDetailView.as_view(), name='note-detail'),
]
