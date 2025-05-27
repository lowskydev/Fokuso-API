"""
Serializers for the Flashcard model.
"""
from rest_framework import serializers
from core.models import Flashcard, Deck


class DeckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deck
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class FlashcardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flashcard
        fields = [
            'id', 'question', 'answer', 'deck', 'next_review',
            'interval', 'ease_factor', 'repetition',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_deck(self, value):
        # Only allow decks belonging to the authenticated user
        user = self.context['request'].user
        if value.owner != user:
            raise serializers.ValidationError(
                "You can only assign flashcards to your own decks."
                )
        return value


class FlashcardListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flashcard
        fields = ['id', 'question', 'answer', 'deck']
