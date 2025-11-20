from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Студент'),
        ('teacher', 'Преподаватель'),
        ('admin', 'Администратор'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    
    class Meta:
        db_table = 'users'

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)
    moodle_id = models.CharField(max_length=100, unique=True)
    duration_hours = models.IntegerField(default=40)
    difficulty = models.CharField(max_length=50, default='medium')
    x_position = models.FloatField(default=0.0)
    y_position = models.FloatField(default=0.0)
    z_position = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'courses'
    
    def __str__(self):
        return self.title

class Trajectory(models.Model):
    TRAJECTORY_TYPE = [
        ('personal', 'Личная траектория'),
        ('teacher', 'Траектория преподавателя'),
    ]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trajectories')
    name = models.CharField(max_length=255)
    trajectory_type = models.CharField(max_length=20, choices=TRAJECTORY_TYPE)
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_trajectories')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'trajectories'
    
    def __str__(self):
        return f"{self.name} - {self.student.username}"

class TrajectoryCourse(models.Model):
    trajectory = models.ForeignKey(Trajectory, on_delete=models.CASCADE, related_name='courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    status = models.CharField(max_length=50, default='not_started')
    progress = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'trajectory_courses'
        ordering = ['order']
        unique_together = ['trajectory', 'course']
    
    def __str__(self):
        return f"{self.trajectory.name} - {self.course.title}"

class StudentProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    progress_percent = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'student_progress'
        unique_together = ['student', 'course']
    
    def __str__(self):
        return f"{self.student.username} - {self.course.title} - {self.progress_percent}%"
