from django.shortcuts import render

# Create your views here.
from task.models import Task, UserProfile
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout


def is_admin(user):
    try:
        return user.profile.role == 'admin'
    except UserProfile.DoesNotExist:
        return False

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None and is_admin(user):
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid admin credentials or insufficient permissions')
    
    return render(request, 'login.html')



def admin_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('a_login')


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    user = request.user
    # recent_tasks = Task.objects.filter(created_by=user).order_by('-id')[:5]

    if user.is_superuser:
        recent_tasks = Task.objects.all().order_by('-id')[:5]
    else:
        assigned_users = User.objects.filter(profile__assigned_admin=user)
        recent_tasks = Task.objects.filter(
            Q(created_by=user) | Q(assigned_to__in=assigned_users)
        ).order_by('-id')[:5]
    
    if user.is_superuser:
        total_users = User.objects.filter(is_superuser=False).count()
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
    
    context = {
        'total_users': total_users,
        'total_admins': total_admins,
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
        'completed_tasks': completed_tasks,
        'recent_tasks': recent_tasks
    }
    return render(request, 'dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def admin_tasks_list(request):
    user = request.user
    
    # if user.is_superuser:
    #     tasks = Task.objects.all().order_by('-id')
    # else:
    #     assigned_users = User.objects.filter(profile__assigned_admin=user)
    #     tasks = Task.objects.filter(
    #         Q(assigned_to__in=assigned_users) | 
    #         Q(created_by=user) |
    #         Q(assigned_to=user)
    #     )


    if user.is_superuser:
        tasks = Task.objects.all().order_by('-id')
    else:
        assigned_users = User.objects.filter(profile__assigned_admin=user)
        tasks = Task.objects.filter(
            Q(created_by=user) | Q(assigned_to__in=assigned_users)
        ).order_by('-id')
    
    context = {'tasks': tasks}
    return render(request, 'task/tasks_list.html', context)


@login_required
@user_passes_test(is_admin)
def admin_create_task(request):
    user = request.user
    
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
        return redirect('admin_tasks_list')
    
    # Show all regular users (non-superuser, role='user') regardless of who is logged in
    assignable_users = User.objects.filter(
        is_superuser=False,
        profile__role='user'
    )

    
    context = {'assignable_users': assignable_users}
    return render(request, 'task/create_task.html', context)


@login_required
@user_passes_test(is_admin)
def admin_edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    user = request.user
    
   
    if not (user.is_superuser or 
            (hasattr(user, 'profile') and user.profile.role == 'admin' and 
             (task.assigned_to.profile.assigned_admin == user if task.assigned_to else False)) or
            task.created_by == user):
        messages.error(request, 'Permission denied')
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        task.title = request.POST.get('title')
        task.description = request.POST.get('description')
        
        assigned_to_id = request.POST.get('assigned_to')
        task.assigned_to_id = assigned_to_id
        
        task.due_date = request.POST.get('due_date')
        task.status = request.POST.get('status')
        
        if task.status == 'completed':
            completion_report = request.POST.get('completion_report')
            worked_hours = request.POST.get('worked_hours')
            
            if not completion_report or not worked_hours:
                messages.error(request, 'Completion report and worked hours are required when marking a task as completed')
                return redirect('admin_edit_task', task_id=task.id)
            
            task.completion_report = completion_report
            task.worked_hours = worked_hours
        
        task.save()
        messages.success(request, 'Task updated successfully')
        return redirect('admin_tasks_list')
    
    # if user.is_superuser:
    #     assignable_users = User.objects.all()
    # else:
    #     assignable_users = User.objects.filter(
    #         Q(profile__assigned_admin=user) | 
    #         Q(id=user.id)
    #     )

    assignable_users = User.objects.filter(
        is_superuser=False,
        profile__role='user'
    )
    
    context = {
        'task': task,
        'assignable_users': assignable_users
    }
    return render(request, 'task/edit_task.html', context)


@login_required
@user_passes_test(is_admin)
def admin_delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    user = request.user
    
   
    if not (user.is_superuser or 
            (hasattr(user, 'profile') and user.profile.role == 'admin' and 
             (task.assigned_to.profile.assigned_admin == user if task.assigned_to else False)) or
            task.created_by == user):
        messages.error(request, 'Permission denied')
        return redirect('admin_dashboard')
    
    task.delete()
    messages.success(request, 'Task deleted successfully')
    return redirect('admin_tasks_list')


@login_required
@user_passes_test(is_admin)
def admin_view_task_report(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    user = request.user
    
   
    if not (user.is_superuser or 
            (hasattr(user, 'profile') and user.profile.role == 'admin' and 
             (task.assigned_to.profile.assigned_admin == user if task.assigned_to else False)) or
            task.created_by == user):
        messages.error(request, 'Permission denied')
        return redirect('admin_dashboard')
    
    if task.status != 'completed':
        messages.error(request, 'Task report is only available for completed tasks')
        return redirect('admin_tasks_list')
    
    context = {'task': task}
    return render(request, 'task/task_report.html', context)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_users_list(request):
    users = User.objects.all()
    context = {'users': users}
    return render(request, 'users/users_list.html', context)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_create_user(request):
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
            return redirect('admin_create_user')
        
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
        return redirect('admin_users_list')
    
    admins = User.objects.filter(profile__role='admin')
    context = {'admins': admins}
    return render(request, 'admin_app/create_user.html', context)