from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Course, Trajectory, TrajectoryCourse, StudentProgress

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'is_staff']
    list_filter = ['role', 'is_staff']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('role',)}),
    )

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'moodle_id', 'duration_hours', 'difficulty']
    list_filter = ['category', 'difficulty']
    search_fields = ['title', 'moodle_id']

@admin.register(Trajectory)
class TrajectoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'student', 'trajectory_type', 'teacher', 'created_at']
    list_filter = ['trajectory_type']
    search_fields = ['name', 'student__username']

@admin.register(TrajectoryCourse)
class TrajectoryCourseAdmin(admin.ModelAdmin):
    list_display = ['trajectory', 'course', 'order', 'status', 'progress']
    list_filter = ['status']

@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'progress_percent', 'completed', 'started_at']
    list_filter = ['completed']
    search_fields = ['student__username', 'course__title']
