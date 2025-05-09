from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile, Task
from django.db.models import Q
from datetime import datetime

def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful')
            return redirect('index')
        else:
            messages.error(request, 'Invalid username or password')
            return render(request, 'login.html')
    return render(request, 'login.html')

@login_required
def signout(request):
    logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('signin')

@login_required
def index(request):
   
    user = request.user
    recent_tasks = Task.objects.all().order_by('-id')[:5]
    
    if user.is_superuser:
    
        total_users = UserProfile.objects.filter(role='user', user__is_superuser=False).count()
        total_admins = UserProfile.objects.filter(role='admin').count()
        total_tasks = Task.objects.all().count()
        pending_tasks = Task.objects.filter(status='pending').count()
        completed_tasks = Task.objects.filter(status='completed').count()
    elif hasattr(user, 'profile') and user.profile.role == 'admin':
       
        assigned_users = User.objects.filter(profile__assigned_admin=user)
        total_users = assigned_users.count()
        total_admins = 0  
        total_tasks = Task.objects.filter(
            Q(assigned_to__in=assigned_users) | Q(created_by=user)
        ).count()
        pending_tasks = Task.objects.filter(
            Q(assigned_to__in=assigned_users) | Q(created_by=user),
            status='pending'
        ).count()
        completed_tasks = Task.objects.filter(
            Q(assigned_to__in=assigned_users) | Q(created_by=user),
            status='completed'
        ).count()
    else:
        
        total_users = 0
        total_admins = 0
        total_tasks = Task.objects.filter(assigned_to=user).count()
        pending_tasks = Task.objects.filter(assigned_to=user, status='pending').count()
        completed_tasks = Task.objects.filter(assigned_to=user, status='completed').count()
    
    context = {
        'total_users': total_users,
        'total_admins': total_admins,
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
        'completed_tasks': completed_tasks,
        'recent_tasks':recent_tasks
    }
    return render(request, 'index.html', context)


@login_required
def users_list(request):
    if not request.user.is_superuser:
        messages.error(request, 'Permission denied')
        return redirect('index')
    
    users = User.objects.filter(is_superuser=False).order_by('-id')
    admins = User.objects.filter(profile__role='admin').order_by('-id')
    
    context = {
        'users': users,
        'admins': admins
    }
    return render(request, 'users/users_list.html', context)

@login_required
def create_user(request):
    if not request.user.is_superuser:
        messages.error(request, 'Permission denied')
        return redirect('index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role')
        assigned_admin_id = request.POST.get('assigned_admin')
        
       
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('create_user')
        
       
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
    
        profile = UserProfile(user=user, role=role)
        
        if role == 'user' and assigned_admin_id:
            admin = User.objects.get(id=assigned_admin_id)
            profile.assigned_admin = admin
        
        profile.save()
        messages.success(request, f'User {username} created successfully')
        return redirect('users_list')
    
 
    admins = User.objects.filter(profile__role='admin')
    context = {'admins': admins}
    return render(request, 'users/create_user.html', context)

@login_required
def edit_user(request, user_id):
    if not request.user.is_superuser:
        messages.error(request, 'Permission denied')
        return redirect('index')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
       
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        
        
        password = request.POST.get('password')
        if password:
            user.set_password(password)
            
        user.save()
        
      
        profile = user.profile
        profile.role = request.POST.get('role')
        
        if profile.role == 'user':
            assigned_admin_id = request.POST.get('assigned_admin')
            if assigned_admin_id:
                profile.assigned_admin = User.objects.get(id=assigned_admin_id)
            else:
                profile.assigned_admin = None
        else:
            profile.assigned_admin = None
        
        profile.save()
        messages.success(request, f'User {user.username} updated successfully')
        return redirect('users_list')
    
   
    admins = User.objects.filter(profile__role='admin')
    context = {
        'user_obj': user,
        'admins': admins
    }
    return render(request, 'users/edit_user.html', context)

@login_required
def delete_user(request, user_id):
    if not request.user.is_superuser:
        messages.error(request, 'Permission denied')
        return redirect('index')
    
    user = get_object_or_404(User, id=user_id)
    username = user.username
    user.delete()
    messages.success(request, f'User {username} deleted successfully')
    return redirect('users_list')

@login_required
def assign_admin(request, user_id):
    if not request.user.is_superuser:
        messages.error(request, 'Permission denied')
        return redirect('index')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        admin_id = request.POST.get('admin_id')
        admin = User.objects.get(id=admin_id)
        
        profile = user.profile
        profile.assigned_admin = admin
        profile.save()
        
        messages.success(request, f'User {user.username} assigned to admin {admin.username}')
    
    return redirect('users_list')


@login_required
def tasks_list(request):
    user = request.user
    
    if user.is_superuser:
 
        tasks = Task.objects.all().order_by('-id')
    elif hasattr(user, 'profile') and user.profile.role == 'admin':
      
        assigned_users = User.objects.filter(profile__assigned_admin=user)
        tasks = Task.objects.filter(
            Q(assigned_to__in=assigned_users) | 
            Q(created_by=user) |
            Q(assigned_to=user)
        )
    else:
      
        tasks = Task.objects.filter(assigned_to=user)
    
    context = {'tasks': tasks}
    return render(request, 'tasks/tasks_list.html', context)

@login_required
def create_task(request):
    user = request.user
    

    if not (user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'admin')):
        messages.error(request, 'Permission denied')
        return redirect('index')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        assigned_to_id = request.POST.get('assigned_to')
        due_date = request.POST.get('due_date')
        status = request.POST.get('status')
        
       
        task = Task(
            title=title,
            description=description,
            assigned_to_id=assigned_to_id,
            created_by=user,
            due_date=due_date,
            status=status
        )
        task.save()
        
        messages.success(request, 'Task created successfully')
        return redirect('tasks_list')
    
  
    # if user.is_superuser:
    #     assignable_users = User.objects.all()
    # else: 
    #     assignable_users = User.objects.filter(
    #         Q(profile__assigned_admin=user) | 
    #         Q(id=user.id)
    #     )

    if user.is_superuser:
        assignable_users = User.objects.filter(
            is_superuser=False,
            profile__role='user'
        )
    else:
        assignable_users = User.objects.filter(
            Q(profile__assigned_admin=user) | Q(id=user.id),
            is_superuser=False,
            profile__role='user'
        )
    
    context = {'assignable_users': assignable_users}
    return render(request, 'tasks/create_task.html', context)

@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    user = request.user
    
   
    if not (user.is_superuser or 
            (hasattr(user, 'profile') and user.profile.role == 'admin' and 
             (task.assigned_to.profile.assigned_admin == user if task.assigned_to else False)) or
            task.created_by == user or
            task.assigned_to == user):
        messages.error(request, 'Permission denied')
        return redirect('index')
    
    if request.method == 'POST':
        task.title = request.POST.get('title')
        task.description = request.POST.get('description')
        
      
        if user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'admin'):
            assigned_to_id = request.POST.get('assigned_to')
            task.assigned_to_id = assigned_to_id
        
        task.due_date = request.POST.get('due_date')
        task.status = request.POST.get('status')
        

        if task.status == 'completed':
            completion_report = request.POST.get('completion_report')
            worked_hours = request.POST.get('worked_hours')
            
            if not completion_report or not worked_hours:
                messages.error(request, 'Completion report and worked hours are required when marking a task as completed')
                return redirect('edit_task', task_id=task.id)
            
            task.completion_report = completion_report
            task.worked_hours = worked_hours
        
        task.save()
        messages.success(request, 'Task updated successfully')
        return redirect('tasks_list')
    
   
    # if user.is_superuser:
    #     assignable_users = User.objects.all()
    # elif hasattr(user, 'profile') and user.profile.role == 'admin':
    #     assignable_users = User.objects.filter(
    #         Q(profile__assigned_admin=user) | 
    #         Q(id=user.id)
    #     )
    # else:
    #     assignable_users = []

    if user.is_superuser:
        assignable_users = User.objects.filter(
            is_superuser=False,
            profile__role='user'
        )
    else:
        assignable_users = User.objects.filter(
            Q(profile__assigned_admin=user) | Q(id=user.id),
            is_superuser=False,
            profile__role='user'
        )
    
    context = {
        'task': task,
        'assignable_users': assignable_users
    }
    return render(request, 'tasks/edit_task.html', context)

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    user = request.user
    
  
    if not (user.is_superuser or 
            (hasattr(user, 'profile') and user.profile.role == 'admin' and 
             (task.assigned_to.profile.assigned_admin == user if task.assigned_to else False)) or
            task.created_by == user):
        messages.error(request, 'Permission denied')
        return redirect('index')
    
    task.delete()
    messages.success(request, 'Task deleted successfully')
    return redirect('tasks_list')

@login_required
def view_task_report(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    user = request.user
    
 
    if not (user.is_superuser or 
            (hasattr(user, 'profile') and user.profile.role == 'admin' and 
             (task.assigned_to.profile.assigned_admin == user if task.assigned_to else False)) or
            task.created_by == user or
            task.assigned_to == user):
        messages.error(request, 'Permission denied')
        return redirect('index')
    

    if task.status != 'completed':
        messages.error(request, 'Task report is only available for completed tasks')
        return redirect('tasks_list')
    
    context = {'task': task}
    return render(request, 'tasks/task_report.html', context)

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    user = request.user
    
 
    if task.assigned_to != user:
        messages.error(request, 'Permission denied')
        return redirect('index')
    
    if request.method == 'POST':
        completion_report = request.POST.get('completion_report')
        worked_hours = request.POST.get('worked_hours')
        
        if not completion_report or not worked_hours:
            messages.error(request, 'Completion report and worked hours are required')
            return redirect('complete_task', task_id=task.id)
        
        task.status = 'completed'
        task.completion_report = completion_report
        task.worked_hours = worked_hours
        task.save()
        
        messages.success(request, 'Task marked as completed')
        return redirect('tasks_list')
    
    context = {'task': task}
    return render(request, 'tasks/complete_task.html', context)