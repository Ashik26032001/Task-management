from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    assigned_admin = models.ForeignKey(User, related_name='assigned_users', 
                                      on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} ({self.role})"
    


class Task(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )
    
    title = models.CharField(max_length=200,blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    assigned_to = models.ForeignKey(User, related_name='assigned_tasks', on_delete=models.CASCADE,blank=True, null=True)
    created_by = models.ForeignKey(User, related_name='created_tasks', on_delete=models.CASCADE,blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    completion_report = models.TextField(blank=True, null=True)
    worked_hours = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
        
    class Meta:
        ordering = ['-created_at']
