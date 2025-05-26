"""
Views for the flashcards app.
"""
from rest_framework import generics

from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from core.models import Flashcard

from flashcards.serializers import FlashcardSerializer, FlashcardListSerializer


class FlashcardListCreateView(generics.ListCreateAPIView):
    """
    A viewset for viewing and editing flashcards.
    """
    serializer_class = FlashcardSerializer
    queryset = Flashcard.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        """Retrive flashcards for the authenticated user."""
        return self.queryset.filter(
            owner=self.request.user
            ).order_by('created_at')

    def get_serializer_class(self):
        """Return the appropriate serializer class based on the action."""
        if self.request.method == 'GET':
            return FlashcardListSerializer
        return FlashcardSerializer

    def perform_create(self, serializer):
        """Assign the flashcard to the authenticated user."""
        serializer.save(owner=self.request.user)


class FlashcardsDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    A viewset for viewing and editing flashcards.
    """
    serializer_class = FlashcardSerializer
    queryset = Flashcard.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        """Retrive flashcards for the authenticated user."""
        return self.queryset.filter(
            owner=self.request.user
            ).order_by('created_at')
