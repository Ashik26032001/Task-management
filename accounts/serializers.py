from rest_framework import serializers
from task.models import Task
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class TaskSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'assigned_to', 'created_by',
            'due_date', 'status', 'completion_report', 'worked_hours',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by']

    def validate(self, data):
        if data.get('status') == 'completed':
            if not data.get('completion_report') or not data.get('worked_hours'):
                raise serializers.ValidationError(
                    "Completion report and worked hours are required when marking a task as completed"
                )
            if data.get('worked_hours') <= 0:
                raise serializers.ValidationError(
                    "Worked hours must be a positive number"
                )
        return data

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)