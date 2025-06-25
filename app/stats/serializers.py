from rest_framework import serializers
from core.models import FocusSession

class FocusSessionSerializer(serializers.ModelSerializer):
    class Meta:
        Model = FocusSession
        fields = ['id', 'user', 'session_type', 'duration', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
        