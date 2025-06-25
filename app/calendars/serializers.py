"""
Serializers for the Calendars API.
"""
from rest_framework import serializers
from core.models import Event
from datetime import datetime


class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event objects"""
    time = serializers.ReadOnlyField()
    endTime = serializers.CharField(
        source='end_time_formatted',
        read_only=True
    )
    duration = serializers.ReadOnlyField()
    type = serializers.CharField(source='event_type')

    class Meta:
        model = Event
        fields = [
            'id',
            'title',
            'description',
            'date',
            'start_time',
            'end_time',
            'time',
            'endTime',
            'event_type',
            'type',
            'duration',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id',
                            'created_at',
                            'updated_at',
                            'time',
                            'endTime',
                            'duration'
                            ]

    def validate(self, data):
        """Validate that end_time is after start_time"""
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        if start_time and end_time:
            # Convert to datetime for comparison
            start_datetime = datetime.combine(
                datetime.today().date(),
                start_time
            )
            end_datetime = datetime.combine(
                datetime.today().date(),
                end_time
            )

            if end_datetime <= start_datetime:
                raise serializers.ValidationError(
                    "End time must be after start time."
                )

        return data


class EventCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating events"""
    type = serializers.CharField(
        source='event_type',
        required=False
    )

    class Meta:
        model = Event
        fields = [
            'title',
            'description',
            'date',
            'start_time',
            'end_time',
            'event_type',
            'type'
        ]

    def validate(self, data):
        """Validate that end_time is after start_time"""
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        if start_time and end_time:
            start_datetime = datetime.combine(
                datetime.today().date(),
                start_time
            )
            end_datetime = datetime.combine(
                datetime.today().date(),
                end_time
            )

            if end_datetime <= start_datetime:
                raise serializers.ValidationError(
                    "End time must be after start time."
                )

        return data


class EventListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing events"""
    time = serializers.ReadOnlyField()
    endTime = serializers.CharField(
        source='end_time_formatted',
        read_only=True
    )
    duration = serializers.ReadOnlyField()
    type = serializers.CharField(source='event_type')

    class Meta:
        model = Event
        fields = [
            'id',
            'title',
            'date',
            'time',
            'endTime',
            'type',
            'duration'
        ]
