"""
Serializers for the Flashcard model.
"""
from rest_framework import serializers
from core.models import (
    Flashcard,
    Deck,
    ReviewLog,
)


class DeckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deck
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class FlashcardSerializer(serializers.ModelSerializer):
    interval_display = serializers.CharField(read_only=True)  # Add human-readable interval

    class Meta:
        model = Flashcard
        fields = [
            'id', 'question', 'answer', 'deck', 'next_review',
            'interval', 'interval_display', 'ease_factor', 'repetition', 'is_learning',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'interval_display']

    def validate_deck(self, value):
        # Only allow decks belonging to the authenticated user
        user = self.context['request'].user
        if value and value.owner != user:
            raise serializers.ValidationError(
                "You can only assign flashcards to your own decks."
            )
        return value


class FlashcardListSerializer(serializers.ModelSerializer):
    interval_display = serializers.CharField(read_only=True)

    class Meta:
        model = Flashcard
        fields = ['id', 'deck', 'question', 'answer', 'next_review', 'interval_display', 'is_learning']


class FlashcardReviewSerializer(serializers.Serializer):
    grade = serializers.IntegerField(min_value=1, max_value=3)  # Changed to 1-3
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
