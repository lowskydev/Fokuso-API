"""
URLs for the calendar app.
"""
from django.urls import path
from calendar.views import (
    EventListCreateView,
    EventDetailView,
    EventsGroupedByDateView,
    TodayEventsView,
)

app_name = 'calendar'

urlpatterns = [
    # Event endpoints
    path('events/', EventListCreateView.as_view(), name='event-list-create'),
    path('events/<int:pk>/', EventDetailView.as_view(), name='event-detail'),

    # Special endpoints
    path(
        'events/grouped/',
        EventsGroupedByDateView.as_view(),
        name='events-grouped'
    ),
    path('events/today/', TodayEventsView.as_view(), name='today-events'),
]
