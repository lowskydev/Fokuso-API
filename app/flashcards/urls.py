"""
Urls for the flashcards app.
"""
from django.urls import path
from .views import FlashcardListCreateView, FlashcardsDetailView

urlpatterns = [
    path('', FlashcardListCreateView.as_view(), name='flashcard-list-create'),
    path('<int:pk>/', FlashcardsDetailView.as_view(), name='flashcard-detail'),
]
