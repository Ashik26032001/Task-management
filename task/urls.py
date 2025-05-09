from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('', views.signin, name='signin'),
    path('logout/', views.signout, name='signout'),
    path('index/', views.index, name='index'),
    

    path('users/', views.users_list, name='users_list'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('users/assign-admin/<int:user_id>/', views.assign_admin, name='assign_admin'),
    

    path('tasks/', views.tasks_list, name='tasks_list'),
    path('tasks/create/', views.create_task, name='create_task'),
    path('tasks/edit/<int:task_id>/', views.edit_task, name='edit_task'),
    path('tasks/delete/<int:task_id>/', views.delete_task, name='delete_task'),
    path('tasks/report/<int:task_id>/', views.view_task_report, name='view_task_report'),
    path('tasks/complete/<int:task_id>/', views.complete_task, name='complete_task'),
    
]
