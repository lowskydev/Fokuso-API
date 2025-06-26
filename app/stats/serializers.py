from rest_framework import serializers
from core.models import FocusSession


class FocusSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FocusSession  # Fixed: was "Model"
        fields = [
            'id', 'owner', 'session_type', 'duration', 'created_at'
            ]  # Fixed: was 'user'
        read_only_fields = ['id', 'owner', 'created_at']  # Fixed: was 'user'


class UserStatsSerializer(serializers.Serializer):
    totalSessions = serializers.IntegerField()
    totalFocusTime = serializers.IntegerField()
    todayFocusTime = serializers.IntegerField()
    currentStreak = serializers.IntegerField()
    longestStreak = serializers.IntegerField()
    averageSessionLength = serializers.IntegerField()
    thisWeekSessions = serializers.IntegerField()
    thisMonthSessions = serializers.IntegerField()
    totalBreakTime = serializers.IntegerField()


class WeeklyDataSerializer(serializers.Serializer):
    day = serializers.CharField()
    sessions = serializers.IntegerField()
    focusTime = serializers.IntegerField()


class HourlyDataSerializer(serializers.Serializer):
    hour = serializers.CharField()
    sessions = serializers.IntegerField()
