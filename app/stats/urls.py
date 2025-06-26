from django.urls import path
from .views import (
    CreateFocusSessionView,
    UserStatsView,
    WeeklyDataView,
    HourlyDataView,
)

urlpatterns = [
    path('session/', CreateFocusSessionView.as_view(), name='create-session'),
    path('user-stats/', UserStatsView.as_view(), name='user-stats'),
    path('weekly-data/', WeeklyDataView.as_view(), name='weekly-data'),
    path('hourly-data/', HourlyDataView.as_view(), name='hourly-data'),
]
