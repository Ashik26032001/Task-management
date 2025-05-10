from django.urls import path
from .views import  TaskListView, TaskUpdateView, TaskReportView
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserLoginView, 
    AdminLoginView,
    SuperadminLoginView,
   
)


urlpatterns = [
    
    path('login/user/', UserLoginView.as_view(), name='user_login'),
    path('login/admin/', AdminLoginView.as_view(), name='admin_login'),
    path('login/superadmin/', SuperadminLoginView.as_view(), name='superadmin_login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('tasks/', TaskListView.as_view(), name='task_list'),
    path('tasks/<int:id>/', TaskUpdateView.as_view(), name='task_update'),
    path('tasks/<int:id>/report/', TaskReportView.as_view(), name='task_report'),
    
    
]
