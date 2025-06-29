"""
Serializers for the Flashcard model.
"""
from rest_framework import serializers
from core.models import (
    Flashcard,
    Deck,
    ReviewLog,
    DailyReviewStats
)

from drf_spectacular.utils import extend_schema_field


class DeckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deck
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class FlashcardSerializer(serializers.ModelSerializer):
    interval_display = serializers.CharField(read_only=True)

    class Meta:
        model = Flashcard
        fields = [
            'id',
            'question',
            'answer',
            'deck',
            'next_review',
            'interval',
            'interval_display',
            'ease_factor',
            'repetition',
            'is_learning',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'next_review',
            'interval',
            'interval_display',
            'ease_factor',
            'repetition',
            'is_learning',
            'created_at',
            'updated_at'
        ]

    def validate_deck(self, value):
        # Deck is required
        if not value:
            raise serializers.ValidationError("Deck is required.")

        # Only allow decks belonging to the authenticated user
        user = self.context['request'].user
        if value.owner != user:
            raise serializers.ValidationError(
                "You can only assign flashcards to your own decks."
            )
        return value


class FlashcardCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating flashcards"""

    class Meta:
        model = Flashcard
        fields = ['question', 'answer', 'deck']

    def validate_deck(self, value):
        # Deck is required
        if not value:
            raise serializers.ValidationError("Deck is required.")

        # Only allow decks belonging to the authenticated user
        user = self.context['request'].user
        if value.owner != user:
            raise serializers.ValidationError(
                "You can only assign flashcards to your own decks."
            )
        return value


class FlashcardListSerializer(serializers.ModelSerializer):
    interval_display = serializers.CharField(read_only=True)

    class Meta:
        model = Flashcard
        fields = [
            'id',
            'deck',
            'question',
            'answer',
            'next_review',
            'interval_display',
            'is_learning'
        ]


class FlashcardReviewSerializer(serializers.Serializer):
    # Changed to 1-3
    grade = serializers.IntegerField(min_value=1, max_value=3)
    new_interval = serializers.IntegerField(read_only=True)
    new_interval_display = serializers.CharField(read_only=True)
    new_ease_factor = serializers.IntegerField(read_only=True)
    new_repetition = serializers.IntegerField(read_only=True)
    new_next_review = serializers.DateTimeField(read_only=True)
    is_learning = serializers.BooleanField(read_only=True)


class ReviewLogSerializer(serializers.ModelSerializer):
    flashcard_id = serializers.IntegerField(
        source='flashcard.id',
        read_only=True,
    )
    user_id = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = ReviewLog
        fields = ['id', 'flashcard_id', 'user_id', 'reviewed_at', 'grade']
        read_only_fields = fields


class DailyReviewStatsSerializer(serializers.ModelSerializer):
    @extend_schema_field(serializers.FloatField)
    def get_accuracy_percentage(self, obj):
        return obj.accuracy_percentage

    accuracy_percentage = serializers.SerializerMethodField()

    class Meta:
        model = DailyReviewStats
        fields = [
            'id',
            'date',
            'flashcards_reviewed',
            'correct_reviews',
            'incorrect_reviews',
            'accuracy_percentage',
            'total_review_time_minutes'
        ]
        read_only_fields = ['id']
