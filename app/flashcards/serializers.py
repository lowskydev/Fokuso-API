"""
Serializers for the Flashcard model.
"""
from rest_framework import serializers
from core.models import Flashcard


class FlashcardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flashcard
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
