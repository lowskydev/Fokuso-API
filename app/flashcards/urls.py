"""
Urls for the flashcards app.
"""
from django.urls import path
from .views import (
    FlashcardListCreateView,
    FlashcardsDetailView,
    DeckListCreateView,
    DeckDetailView,
    FlashcardReviewView,
)

app_name = 'flashcards'

urlpatterns = [
    # Deck Endpoints
    path('decks/', DeckListCreateView.as_view(), name='deck-list-create'),
    path('decks/<int:pk>/', DeckDetailView.as_view(), name='deck-detail'),

    # Flashcard Endpoints
    path('', FlashcardListCreateView.as_view(), name='flashcard-list-create'),
    path('<int:pk>/', FlashcardsDetailView.as_view(), name='flashcard-detail'),

    # Flashcard Review Endpoint
    path('<int:pk>/review/',
         FlashcardReviewView.as_view(),
         name='flashcard-review',
         ),
]
