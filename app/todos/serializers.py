"""
Serializers for the Todo API.
"""
from rest_framework import serializers
from core.models import Todo, Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag objects"""

    class Meta:
        model = Tag
        fields = ['id', 'name', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_name(self, value):
        """Validate that tag name is unique for the user"""
        user = self.context['request'].user
        if Tag.objects.filter(owner=user, name__iexact=value).exists():
            # If we're updating, exclude the current instance
            if self.instance:
                if Tag.objects.filter(
                    owner=user,
                    name__iexact=value
                ).exclude(id=self.instance.id).exists():
                    raise serializers.ValidationError(
                        "You already have a tag with this name."
                    )
            else:
                raise serializers.ValidationError(
                    "You already have a tag with this name."
                )
        return value.lower().strip()


class TodoListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing todos"""
    tags = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Todo
        fields = [
            'id', 'title', 'description', 'completed', 'priority',
            'category', 'due_date', 'tags', 'created_at'
        ]


class TodoDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for todo CRUD operations"""
    tags = TagSerializer(many=True, read_only=True)
    tag_names = serializers.ListField(
        child=serializers.CharField(max_length=50),
        write_only=True,
        required=False,
        allow_empty=True
    )

    class Meta:
        model = Todo
        fields = [
            'id', 'title', 'description', 'completed', 'priority',
            'category', 'due_date', 'tags', 'tag_names', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        """Create todo with tags"""
        tag_names = validated_data.pop('tag_names', [])
        user = self.context['request'].user

        # Create the todo
        todo = Todo.objects.create(owner=user, **validated_data)

        # Handle tags
        self._handle_tags(todo, tag_names, user)

        return todo

    def update(self, instance, validated_data):
        """Update todo with tags"""
        tag_names = validated_data.pop('tag_names', None)
        user = self.context['request'].user

        # Update the todo
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Handle tags if provided
        if tag_names is not None:
            self._handle_tags(instance, tag_names, user)

        return instance

    def _handle_tags(self, todo, tag_names, user):
        """Helper method to handle tag creation and assignment"""
        if not tag_names:
            todo.tags.clear()
            return

        tag_objects = []
        for tag_name in tag_names:
            tag_name = tag_name.lower().strip()
            if tag_name:  # Only process non-empty tag names
                tag, created = Tag.objects.get_or_create(
                    owner=user,
                    name=tag_name
                )
                tag_objects.append(tag)

        todo.tags.set(tag_objects)


class TodoCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating todos"""
    tag_names = serializers.ListField(
        child=serializers.CharField(max_length=50),
        write_only=True,
        required=False,
        allow_empty=True
    )

    class Meta:
        model = Todo
        fields = [
            'title', 'description', 'priority', 'category', 'due_date', 'tag_names'
        ]

    def create(self, validated_data):
        """Create todo with tags"""
        tag_names = validated_data.pop('tag_names', [])
        user = self.context['request'].user

        # Create the todo
        todo = Todo.objects.create(owner=user, **validated_data)

        # Handle tags
        if tag_names:
            tag_objects = []
            for tag_name in tag_names:
                tag_name = tag_name.lower().strip()
                if tag_name:
                    tag, created = Tag.objects.get_or_create(
                        owner=user,
                        name=tag_name
                    )
                    tag_objects.append(tag)
            todo.tags.set(tag_objects)

        return todo