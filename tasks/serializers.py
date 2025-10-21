from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Shows user email
    
    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'completed', 'created_at', 'updated_at', 'user')
        read_only_fields = ('id', 'created_at', 'updated_at', 'user')

    def create(self, validated_data):
        # Automatically assign the current user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('title', 'description', 'completed')

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty")
        return value.strip()

    def validate_description(self, value):
        return value.strip() if value else ""


class TaskListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views"""
    class Meta:
        model = Task
        fields = ('id', 'title', 'completed', 'created_at', 'updated_at')


class TaskStatsSerializer(serializers.Serializer):
    """Serializer for task statistics"""
    total_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    pending_tasks = serializers.IntegerField()
    completion_rate = serializers.FloatField()






