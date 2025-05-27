"""
Views for the flashcards app.
"""
from rest_framework import generics, status

from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from rest_framework.views import APIView
from rest_framework.response import Response

from core.models import Flashcard, Deck

from flashcards.serializers import (
    FlashcardSerializer,
    FlashcardListSerializer,
    DeckSerializer,
    FlashcardReviewSerializer,
)

from django.utils import timezone
from datetime import timedelta

from flashcards.sm2 import sm2  # Assuming sm2 is a function in flashcards.sm2 module

from rest_framework.generics import GenericAPIView


class DeckListCreateView(generics.ListCreateAPIView):
    """
    A viewset for viewing and creating decks.
    """
    serializer_class = DeckSerializer
    queryset = Deck.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        """Retrive decks for the authenticated user."""
        return self.queryset.filter(
            owner=self.request.user
            ).order_by('updated_at')

    def perform_create(self, serializer):
        """Assign the deck to the authenticated user."""
        serializer.save(
            owner=self.request.user,
        )


class DeckDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    A viewset for viewing and editing decks.
    """
    serializer_class = DeckSerializer
    queryset = Deck.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        """Retrive decks for the authenticated user."""
        return self.queryset.filter(
            owner=self.request.user
            ).order_by('updated_at')


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
        serializer.save(
            owner=self.request.user,
        )


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


class FlashcardReviewView(GenericAPIView):
    serializer_class = FlashcardReviewSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request, pk):
        try:
            flashcard = Flashcard.objects.get(pk=pk, owner=request.user)
        except Flashcard.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = FlashcardReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        grade = serializer.validated_data['grade']

        # Apply SM2
        ef, interval, repetition = sm2(
            grade=grade,
            old_ease_factor=float(flashcard.ease_factor),
            old_interval=flashcard.interval,
            old_repetition=flashcard.repetition
        )

        # Compute new next_review
        new_next_review = timezone.now() + timedelta(days=interval)

        # Save updated values
        flashcard.ease_factor = ef
        flashcard.interval = interval
        flashcard.repetition = repetition
        flashcard.next_review = new_next_review
        flashcard.save()

        response_data = {
            'grade': grade,
            'new_interval': interval,
            'new_ease_factor': ef,
            'new_repetition': repetition,
            'new_next_review': new_next_review,
        }
        return Response(response_data, status=status.HTTP_200_OK)