from django.urls import path
from .views import LoginView, TaskListView, TaskUpdateView, TaskReportView
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('logins/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('tasks/', TaskListView.as_view(), name='task_list'),
    path('tasks/<int:id>/', TaskUpdateView.as_view(), name='task_update'),
    path('tasks/<int:id>/report/', TaskReportView.as_view(), name='task_report'),
    
    
]
