from rest_framework import generics, permissions
from core.models import FocusSession
from .serializers import (
    FocusSessionSerializer,
    UserStatsSerializer,
    WeeklyDataSerializer,
    HourlyDataSerializer,
)
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from rest_framework.authentication import TokenAuthentication


class CreateFocusSessionView(generics.CreateAPIView):
    serializer_class = FocusSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)  # Fixed: was 'user'


class UserStatsView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = UserStatsSerializer  # Add serializer
    # (GenericAPIView requires a serializer class)

    def get(self, request):
        user = request.user
        sessions = FocusSession.objects.filter(
            owner=user
        )  # Fixed: was 'user'

        total_sessions = sessions.count()
        total_focus_time = sessions.filter(
            session_type='focus'
        ).aggregate(total=Sum('duration'))['total'] or 0

        total_break_time = sessions.filter(
            session_type='break'
        ).aggregate(total=Sum('duration'))['total'] or 0

        today = timezone.now().date()
        today_focus_time = sessions.filter(
            session_type='focus',  # Fixed: was 'sessions_type'
            created_at__date=today
        ).aggregate(total=Sum('duration'))['total'] or 0

        focus_dates = sessions.filter(session_type='focus') \
            .values_list('created_at', flat=True)
        focus_days = list({dt.date() for dt in focus_dates})
        # remove duplicates

        current_streak, longest_streak = self.calculate_streaks(
            focus_days
        )

        # Get count of focus sessions only for average calculation
        focus_sessions_count = sessions.filter(
            session_type='focus'
        ).count()

        # Count average of focus session rather than both
        average_session_length = (
            total_focus_time // focus_sessions_count
            if focus_sessions_count else 0
        )

        stats = {
            "totalSessions": total_sessions,
            "totalFocusTime": total_focus_time,
            "todayFocusTime": today_focus_time,
            "currentStreak": current_streak,
            "longestStreak": longest_streak,
            "averageSessionLength": average_session_length,
            "thisWeekSessions": sessions.filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            ).count(),
            "thisMonthSessions": sessions.filter(
                created_at__gte=timezone.now() - timedelta(days=30)
            ).count(),
            "totalBreakTime": total_break_time,
        }
        return Response(stats)

    def calculate_streaks(self, dates):
        if not dates:
            return 0, 0

        dates = sorted(dates, reverse=True)
        today = timezone.now().date()

        current_streak = 0
        longest_streak = 1
        temp_streak = 1

        for i in range(1, len(dates)):
            delta = (dates[i - 1] - dates[i]).days

            if delta == 1:
                temp_streak += 1
                if i == 1 and dates[0] == today:
                    current_streak = temp_streak
            elif delta > 1:
                longest_streak = max(longest_streak, temp_streak)
                temp_streak = 1

        longest_streak = max(longest_streak, temp_streak)

        if dates[0] == today:
            current_streak = temp_streak
        else:
            current_streak = 0

        return current_streak, longest_streak


class WeeklyDataView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = WeeklyDataSerializer

    def get(self, request):
        user = request.user

        # Get the current week (Monday to Sunday)
        today = timezone.now().date()
        monday = today - timedelta(days=today.weekday())

        weekly_data = []
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

        for i, day_name in enumerate(days):
            day_date = monday + timedelta(days=i)

            # Get focus sessions for this day
            day_sessions = FocusSession.objects.filter(
                owner=user,
                session_type='focus',
                created_at__date=day_date
            )

            sessions_count = day_sessions.count()
            focus_time = day_sessions.aggregate(
                total=Sum('duration')
            )['total'] or 0

            weekly_data.append({
                'day': day_name,
                'sessions': sessions_count,
                'focusTime': focus_time
            })

        return Response(weekly_data)


class HourlyDataView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = HourlyDataSerializer

    def get(self, request):
        user = request.user

        # Get all focus sessions for the user
        sessions = FocusSession.objects.filter(
            owner=user,
            session_type='focus'
        )

        # Create hourly data (6 AM to 10 PM)
        hourly_data = []

        # Initialize all hours with 0 sessions
        hour_counts = {}
        for hour in range(6, 23):  # 6 AM to 10 PM
            hour_counts[hour] = 0

        # Count sessions by hour
        for session in sessions:
            hour = session.created_at.hour
            if hour in hour_counts:
                hour_counts[hour] += 1

        # Format the response
        for hour in range(6, 23):
            hourly_data.append({
                'hour': str(hour),
                'sessions': hour_counts[hour]
            })

        return Response(hourly_data)
