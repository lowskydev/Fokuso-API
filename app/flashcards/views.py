"""
Views for the flashcards app.
"""
from rest_framework import (
    viewsets,
    generics,
)

from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from core.models import Flashcard

from serializers import FlashcardSerializer


class FlashcardListViewSet(viewsets.ModelViewSet):
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
            user=self.request.user
            ).order_by('created_at')

    def perform_create(self, serializer):
        """Assign the flashcard to the authenticated user."""
        serializer.save(user=self.request.user)


class FlashcardsDetailViewSet(generics.RetrieveUpdateDestroyAPIView):
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
            user=self.request.user
            ).order_by('created_at')
