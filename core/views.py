from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.http import HttpResponseForbidden
from .models import User, Course, Trajectory, TrajectoryCourse, StudentProgress
import math

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        role = request.POST.get('role', 'student')
        
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Пользователь уже существует'})
        
        user = User.objects.create_user(username=username, password=password, email=email, role=role)
        login(request, user)
        return redirect('dashboard')
    
    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Неверные данные'})
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    user = request.user
    
    # Получаем все курсы для 3D визуализации
    courses = Course.objects.all()
    
    # Траектории пользователя
    trajectories = Trajectory.objects.filter(student=user)
    
    # Прогресс студента
    progress = StudentProgress.objects.filter(student=user)
    
    context = {
        'user': user,
        'courses': courses,
        'trajectories': trajectories,
        'progress': progress,
    }
    
    return render(request, 'dashboard.html', context)

@login_required
def courses_view(request):
    courses_list = Course.objects.all().order_by('-created_at')
    paginator = Paginator(courses_list, 9)
    
    page_number = request.GET.get('page', 1)
    courses_page = paginator.get_page(page_number)
    
    context = {
        'courses': courses_page,
        'user': request.user,
    }
    
    return render(request, 'courses.html', context)

@login_required
def trajectory_view(request, trajectory_id=None):
    user = request.user
    
    if trajectory_id:
        trajectory = get_object_or_404(Trajectory, id=trajectory_id, student=user)
        trajectory_courses = TrajectoryCourse.objects.filter(trajectory=trajectory).select_related('course')
    else:
        trajectory = None
        trajectory_courses = []
    
    all_trajectories = Trajectory.objects.filter(student=user)
    
    context = {
        'user': user,
        'trajectory': trajectory,
        'trajectory_courses': trajectory_courses,
        'all_trajectories': all_trajectories,
    }
    
    return render(request, 'trajectory.html', context)

@login_required
def api_courses(request):
    courses = Course.objects.all()
    data = [{
        'id': c.id,
        'title': c.title,
        'category': c.category,
        'x': c.x_position,
        'y': c.y_position,
        'z': c.z_position,
    } for c in courses]
    return JsonResponse({'courses': data})

@login_required
def create_trajectory(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        trajectory_type = request.POST.get('trajectory_type', 'personal')
        
        trajectory = Trajectory.objects.create(
            student=request.user,
            name=name,
            trajectory_type=trajectory_type
        )
        
        # Добавляем выбранные курсы
        course_ids = request.POST.getlist('courses')
        for idx, course_id in enumerate(course_ids):
            course = Course.objects.get(id=course_id)
            TrajectoryCourse.objects.create(
                trajectory=trajectory,
                course=course,
                order=idx
            )
        
        return redirect('trajectory', trajectory_id=trajectory.id)
    
    courses = Course.objects.all()
    return render(request, 'create_trajectory.html', {'courses': courses})

@login_required
def course_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # Получаем или создаем прогресс пользователя для этого курса
    progress, created = StudentProgress.objects.get_or_create(
        student=request.user,
        course=course,
        defaults={'progress_percent': 0, 'completed': False}
    )
    
    context = {
        'course': course,
        'progress': progress,
    }
    return render(request, 'course.html', context)

@login_required
def delete_trajectory(request, trajectory_id):
    trajectory = get_object_or_404(Trajectory, id=trajectory_id)
    
    # Проверяем, что пользователь может удалять только свои траектории
    if trajectory.student != request.user and not request.user.is_staff:
        return HttpResponseForbidden("Вы не можете удалить эту траекторию")
    
    if request.method == 'POST':
        trajectory.delete()
        return redirect('trajectory_list')
    
    return redirect('trajectory_list')
