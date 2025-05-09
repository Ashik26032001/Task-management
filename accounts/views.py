from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from task.models import Task, UserProfile
from django.contrib.auth.models import User
from .serializers import TaskSerializer, LoginSerializer
from rest_framework.decorators import permission_classes, authentication_classes
from django.db.models import Q
from django.shortcuts import get_object_or_404

class LoginView(APIView):
    permission_classes = [AllowAny] 
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            user = authenticate(username=username, password=password)
            if user is None:
                return Response(
                    {'error': 'Invalid credentials'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class TaskListView(APIView):
    def get(self, request):
        tasks = Task.objects.filter(assigned_to=request.user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class TaskUpdateView(APIView):
    def put(self, request, id):
        task = get_object_or_404(Task, id=id)
        
        if task.assigned_to != request.user:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class TaskReportView(APIView):
    def get(self, request, id):
        task = get_object_or_404(Task, id=id)
        user = request.user
        
        is_admin = hasattr(user, 'profile') and user.profile.role == 'admin'
        is_superadmin = user.is_superuser
        is_assigned_admin = (is_admin and task.assigned_to and 
                           task.assigned_to.profile.assigned_admin == user)
        
        if not (is_superadmin or is_assigned_admin):
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if task.status != 'completed':
            return Response(
                {'error': 'Report only available for completed tasks'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = TaskSerializer(task)
        return Response({
            'task_id': task.id,
            'title': task.title,
            'completion_report': task.completion_report,
            'worked_hours': task.worked_hours,
            'assigned_to': task.assigned_to.username,
            'completed_at': task.updated_at
        }, status=status.HTTP_200_OK)