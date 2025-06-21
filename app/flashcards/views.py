"""
Views for the flashcards app.
"""
from rest_framework import generics, status

from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from rest_framework.response import Response

from core.models import (
    Flashcard,
    Deck,
    ReviewLog,
    DailyReviewStats
)

from flashcards.serializers import (
    FlashcardSerializer,
    FlashcardListSerializer,
    DeckSerializer,
    FlashcardReviewSerializer,
    ReviewLogSerializer,
    FlashcardCreateSerializer,
    DailyReviewStatsSerializer
)

from django.utils import timezone
from datetime import timedelta, date

from flashcards.sm2 import anki_algorithm  # Updated import

from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
)


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
    A viewset for viewing and creating flashcards.
    """
    queryset = Flashcard.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        """
        Retrieve flashcards for the authenticated user.
        """
        return self.queryset.filter(
            owner=self.request.user
            ).order_by('created_at')

    def get_serializer_class(self):
        """
        Return the appropriate serializer class based on the action.
        """
        if self.request.method == 'GET':
            return FlashcardListSerializer
        elif self.request.method == 'POST':
            return FlashcardCreateSerializer  # Use simplified serializer for creation
        return FlashcardSerializer

    def perform_create(self, serializer):
        """Assign the flashcard to the authenticated user."""
        serializer.save(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        """Override create to return full flashcard data after creation"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        flashcard = serializer.save(owner=request.user)

        # Return full flashcard data using the detailed serializer
        response_serializer = FlashcardSerializer(flashcard, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class FlashcardsDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    A viewset for viewing and editing flashcards.
    """
    serializer_class = FlashcardSerializer
    queryset = Flashcard.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        """
        Retrive flashcards for the authenticated user.
        """
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
            return Response(
                {'detail': 'Not found.'},
                status=status.HTTP_404_NOT_FOUND
                )

        serializer = FlashcardReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        grade = serializer.validated_data['grade']

        # Apply Anki algorithm
        ef, interval_minutes, repetition, is_learning = anki_algorithm(
            grade=grade,
            old_ease_factor=flashcard.ease_factor,
            old_interval=flashcard.interval,
            old_repetition=flashcard.repetition,
            is_learning=flashcard.is_learning
        )

        # Compute new next_review based on minutes
        if interval_minutes <= 1:
            # Immediate review (1 minute = now in practice)
            new_next_review = timezone.now()
        else:
            new_next_review = timezone.now() + timedelta(minutes=interval_minutes)

        # Save updated values
        flashcard.ease_factor = ef
        flashcard.interval = interval_minutes
        flashcard.repetition = repetition
        flashcard.is_learning = is_learning
        flashcard.next_review = new_next_review
        flashcard.save()

        # Log the review
        ReviewLog.objects.create(
            flashcard=flashcard,
            user=request.user,
            grade=grade,
        )

        # Helper function for human-readable interval
        def format_interval(minutes):
            if minutes < 60:
                return f"{minutes} minute{'s' if minutes != 1 else ''}"
            elif minutes < 1440:
                hours = minutes // 60
                return f"{hours} hour{'s' if hours != 1 else ''}"
            else:
                days = minutes // 1440
                return f"{days} day{'s' if days != 1 else ''}"

        response_data = {
            'grade': grade,
            'new_interval': interval_minutes,
            'new_interval_display': format_interval(interval_minutes),
            'new_ease_factor': ef,
            'new_repetition': repetition,
            'new_next_review': new_next_review,
            'is_learning': is_learning,
        }
        return Response(response_data, status=status.HTTP_200_OK)


class ReviewLogListView(ListAPIView):
    """
    A viewset for listing review logs.
    """
    serializer_class = ReviewLogSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        """Retrive review logs for the authenticated user."""
        return ReviewLog.objects.filter(
            user=self.request.user
            ).order_by('-reviewed_at')


class FlashcardReviewView(GenericAPIView):
    serializer_class = FlashcardReviewSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request, pk):
        try:
            flashcard = Flashcard.objects.get(pk=pk, owner=request.user)
        except Flashcard.DoesNotExist:
            return Response(
                {'detail': 'Not found.'},
                status=status.HTTP_404_NOT_FOUND
                )

        serializer = FlashcardReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        grade = serializer.validated_data['grade']

        # Apply Anki algorithm
        ef, interval_minutes, repetition, is_learning = anki_algorithm(
            grade=grade,
            old_ease_factor=flashcard.ease_factor,
            old_interval=flashcard.interval,
            old_repetition=flashcard.repetition,
            is_learning=flashcard.is_learning
        )

        # Compute new next_review based on minutes
        if interval_minutes <= 1:
            # Immediate review (1 minute = now in practice)
            new_next_review = timezone.now()
        else:
            new_next_review = timezone.now() + timedelta(minutes=interval_minutes)

        # Save updated values
        flashcard.ease_factor = ef
        flashcard.interval = interval_minutes
        flashcard.repetition = repetition
        flashcard.is_learning = is_learning
        flashcard.next_review = new_next_review
        flashcard.save()

        # Log the review
        ReviewLog.objects.create(
            flashcard=flashcard,
            user=request.user,
            grade=grade,
        )

        # Update daily review stats
        today = date.today()
        daily_stats, created = DailyReviewStats.objects.get_or_create(
            user=request.user,
            date=today,
            defaults={
                'flashcards_reviewed': 0,
                'correct_reviews': 0,
                'incorrect_reviews': 0,
                'total_review_time_minutes': 0,
            }
        )

        # Update the stats
        daily_stats.flashcards_reviewed += 1
        if grade > 1:  # Grade 2 (Good) and 3 (Easy) are considered correct
            daily_stats.correct_reviews += 1
        else:  # Grade 1 (Again) is considered incorrect
            daily_stats.incorrect_reviews += 1

        daily_stats.save()

        # Helper function for human-readable interval
        def format_interval(minutes):
            if minutes < 60:
                return f"{minutes} minute{'s' if minutes != 1 else ''}"
            elif minutes < 1440:
                hours = minutes // 60
                return f"{hours} hour{'s' if hours != 1 else ''}"
            else:
                days = minutes // 1440
                return f"{days} day{'s' if days != 1 else ''}"

        response_data = {
            'grade': grade,
            'new_interval': interval_minutes,
            'new_interval_display': format_interval(interval_minutes),
            'new_ease_factor': ef,
            'new_repetition': repetition,
            'new_next_review': new_next_review,
            'is_learning': is_learning,
            # Include today's review count in response
            'reviews_today': daily_stats.flashcards_reviewed,
        }
        return Response(response_data, status=status.HTTP_200_OK)


# Add new view for getting daily review stats
class DailyReviewStatsView(ListAPIView):
    """
    A view for retrieving daily review statistics.
    """
    serializer_class = DailyReviewStatsSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        """Retrieve daily stats for the authenticated user."""
        # Get query parameters for date range (optional)
        days = self.request.query_params.get('days', 30)  # Default to last 30 days
        try:
            days = int(days)
            days = min(days, 365)  # Limit to 1 year max
        except (ValueError, TypeError):
            days = 30

        from_date = date.today() - timedelta(days=days-1)

        return DailyReviewStats.objects.filter(
            user=self.request.user,
            date__gte=from_date
        ).order_by('-date')


class TodayReviewStatsView(GenericAPIView):
    """
    A view for getting today's review statistics.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        """Get today's review stats for the authenticated user."""
        today = date.today()

        try:
            daily_stats = DailyReviewStats.objects.get(
                user=request.user,
                date=today
            )
            serializer = DailyReviewStatsSerializer(daily_stats)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except DailyReviewStats.DoesNotExist:
            # Return zero stats if no reviews today
            return Response({
                'date': today,
                'flashcards_reviewed': 0,
                'correct_reviews': 0,
                'incorrect_reviews': 0,
                'accuracy_percentage': 0,
                'total_review_time_minutes': 0,
            }, status=status.HTTP_200_OK)