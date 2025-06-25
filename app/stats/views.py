from rest_framework import generics, permissions
from core.models import FocusSession
from .serializers import FocusSessionSerializer
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta

class CreateFocusSessionView(generics.CreateAPIView):
    serializer_class = FocusSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserStatsView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        sessions = FocusSession.objects.filter(user=user)

        total_sessions = sessions.count()
        total_focus_time = sessions.filter(session_type='focus').aggregate_sum('duration') or 0
        total_break_time = sessions.filter(session_type='break').aggregate_sum('duration') or 0

        today = timezone.now().date()
        today_focus_time = sessions.filter(
            sessions_type='focus',
            created_at__date=today
        ).aaggregate_sum('duration') or 0

        focus_dates = sessions.filter(session_type='type') \
              .values_list('created_at', flat=True)
        focus_days = list({dt.date() for dt in focus_dates}) #remove duplicates

        current_streak, longest_streak = self.calculate_streaks(focus_days)

        stats = {
            "totalSessions": total_sessions,
            "totalFocusTime": total_focus_time,
            "todayFocusTime": today_focus_time,
            "currentStreak": current_streak,
            "longestStreak": longest_streak,
            "averageSessionLength": total_focus_time // total_sessions if total_sessions else 0,
            "thisWeekSessions": sessions.filter(
                created_at__gte=timezone.now() - timezone(days=7)
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
        today=timezone.now().date()

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