"""
Views for the todos app.
"""
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from django.db.models import Q

from core.models import Todo, Tag
from todos.serializers import (
    TodoListSerializer,
    TodoDetailSerializer,
    TodoCreateSerializer,
    TagSerializer
)


class TodoListCreateView(generics.ListCreateAPIView):
    """List and create todos for authenticated user"""
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        """Get todos for authenticated user with optional filtering"""
        queryset = Todo.objects.filter(
            owner=self.request.user
            ).prefetch_related('tags')

        # Filter by completion status
        completed = self.request.query_params.get('completed')
        if completed is not None:
            completed_bool = completed.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(completed=completed_bool)

        # Filter by priority
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)

        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)

        # Filter by tags
        tags = self.request.query_params.get('tags')
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            queryset = queryset.filter(tags__name__in=tag_list).distinct()

        # Search in title and description
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )

        return queryset.order_by('-created_at')

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.request.method == 'GET':
            return TodoListSerializer
        return TodoCreateSerializer

    def create(self, request, *args, **kwargs):
        """Create todo and return detailed response"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        todo = serializer.save()

        # Return detailed todo data
        response_serializer = TodoDetailSerializer(
            todo,
            context={'request': request}
        )
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )


class TodoDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete todos"""
    serializer_class = TodoDetailSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        """Get todos for authenticated user"""
        return Todo.objects.filter(
            owner=self.request.user
            ).prefetch_related('tags')


class TagListCreateView(generics.ListCreateAPIView):
    """List and create tags for authenticated user"""
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        """Get tags for authenticated user"""
        return Tag.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        """Create tag for authenticated user"""
        serializer.save(owner=self.request.user)


class TagDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete tags"""
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        """Get tags for authenticated user"""
        return Tag.objects.filter(owner=self.request.user)
