from django.urls import path
from .views import CreateFocusSessionView, UserStatsView

urlpatterns = [
    path('session/', CreateFocusSessionView.as_view(), name='create-session'),
    path('user-stats/', UserStatsView.as_view(), name='user-stats'),
]
