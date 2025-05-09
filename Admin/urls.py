from django.urls import path
from . import views

urlpatterns = [
    # Admin authentication
    # path('login/', views.admin_login, name='admin_login'),
    # path('logout/', views.admin_logout, name='admin_logout'),
    
    # # Admin dashboard
    # path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # # Admin task management
    # path('tasks/', views.admin_tasks_list, name='admin_tasks_list'),
    # path('tasks/create/', views.admin_create_task, name='admin_create_task'),
    # path('tasks/edit/<int:task_id>/', views.admin_edit_task, name='admin_edit_task'),
    # path('tasks/delete/<int:task_id>/', views.admin_delete_task, name='admin_delete_task'),
    # path('tasks/report/<int:task_id>/', views.admin_view_task_report, name='admin_view_task_report'),
    
    # # Admin user management (superuser only)
    # path('users/', views.admin_users_list, name='admin_users_list'),
    # path('users/create/', views.admin_create_user, name='admin_create_user'),
]