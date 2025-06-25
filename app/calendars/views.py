"""
Views for the calendars app.
"""
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from datetime import datetime, date
from collections import defaultdict

from core.models import Event
from calendars.serializers import (  # Changed import
    EventSerializer,
    EventCreateSerializer,
    EventListSerializer
)


class EventListCreateView(generics.ListCreateAPIView):
    """List and create events for authenticated user"""
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        """Get events for authenticated user with optional filtering"""
        queryset = Event.objects.filter(owner=self.request.user)

        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__gte=start_date)
            except ValueError:
                pass

        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__lte=end_date)
            except ValueError:
                pass

        # Filter by specific date
        event_date = self.request.query_params.get('date')
        if event_date:
            try:
                event_date = datetime.strptime(event_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date=event_date)
            except ValueError:
                pass

        # Filter by event type
        event_type = self.request.query_params.get('type')
        if event_type:
            queryset = queryset.filter(event_type=event_type)

        # Search in title and description
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )

        return queryset.order_by('date', 'start_time')

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.request.method == 'GET':
            return EventListSerializer
        return EventCreateSerializer

    def create(self, request, *args, **kwargs):
        """Create event and return detailed response"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = serializer.save(owner=request.user)

        # Return detailed event data
        response_serializer = EventSerializer(
            event,
            context={'request': request}
        )
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete events"""
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        """Get events for authenticated user"""
        return Event.objects.filter(owner=self.request.user)


class EventsGroupedByDateView(APIView):
    """
    Return events grouped by date - matching your frontend format
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        """Get events grouped by date for the authenticated user"""
        queryset = Event.objects.filter(owner=request.user)

        # Filter by date range if provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__gte=start_date)
            except ValueError:
                pass

        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(date__lte=end_date)
            except ValueError:
                pass

        # Filter by event type
        event_type = request.query_params.get('type')
        if event_type:
            queryset = queryset.filter(event_type=event_type)

        events = queryset.order_by('date', 'start_time')

        # Group events by date
        grouped_events = defaultdict(list)
        for event in events:
            date_str = event.date.strftime('%Y-%m-%d')
            event_data = {
                'id': event.id,
                'title': event.title,
                'time': event.time,
                'endTime': event.end_time_formatted,
                'type': event.event_type,
                'duration': event.duration,
            }
            grouped_events[date_str].append(event_data)

        return Response(dict(grouped_events), status=status.HTTP_200_OK)


class TodayEventsView(generics.ListAPIView):
    """Get today's events for the authenticated user"""
    serializer_class = EventListSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        """Get today's events for authenticated user"""
        today = date.today()
        return Event.objects.filter(
            owner=self.request.user,
            date=today
        ).order_by('start_time')
