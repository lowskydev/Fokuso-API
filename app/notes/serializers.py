"""
Serializers for the Note model.
"""
from rest_framework import serializers
from core.models import Note


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'title', 'content', 'created_at', 'updated_at']

        """API can read-only id, created_at and updated-at"""
        read_only_fields = ['id', 'created_at', 'updated_at']
