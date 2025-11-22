from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from .models import User, Course, Trajectory, TrajectoryCourse, StudentProgress
import json

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
    courses = Course.objects.all()
    trajectories = Trajectory.objects.filter(student=user, is_draft=False)
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
        
        courses_by_semester = {}
        for tc in trajectory_courses:
            if tc.semester not in courses_by_semester:
                courses_by_semester[tc.semester] = {'center': [], 'top': [], 'bottom': []}
            courses_by_semester[tc.semester][tc.position].append(tc)
    else:
        trajectory = None
        courses_by_semester = {}
    
    all_trajectories = Trajectory.objects.filter(student=user, is_draft=False)
    
    context = {
        'user': user,
        'trajectory': trajectory,
        'courses_by_semester': courses_by_semester,
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
def trajectory_editor_view(request, trajectory_id=None):
    if trajectory_id:
        trajectory = get_object_or_404(Trajectory, id=trajectory_id, student=request.user, is_draft=True)
        trajectory_courses = TrajectoryCourse.objects.filter(trajectory=trajectory).select_related('course')
        
        existing_data = {}
        for tc in trajectory_courses:
            key = f"{tc.semester}_{tc.position}"
            if key not in existing_data:
                existing_data[key] = []
            existing_data[key].append({
                'course_id': tc.course.id,
                'title': tc.course.title,
                'category': tc.course.category,
                'description': tc.course.description,
                'order': tc.order
            })
    else:
        trajectory = None
        existing_data = {}
    
    all_courses = Course.objects.all().order_by('title')
    
    context = {
        'trajectory': trajectory,
        'all_courses': all_courses,
        'existing_data': json.dumps(existing_data),
    }
    
    return render(request, 'trajectory_editor.html', context)

@login_required
@require_http_methods(["POST"])
def save_trajectory(request):
    data = json.loads(request.body)
    
    trajectory_id = data.get('trajectory_id')
    name = data.get('name')
    courses_data = data.get('courses', [])
    
    if trajectory_id:
        trajectory = get_object_or_404(Trajectory, id=trajectory_id, student=request.user)
    else:
        trajectory = Trajectory.objects.create(
            student=request.user,
            name=name,
            trajectory_type='personal',
            is_draft=False
        )
    
    trajectory.name = name
    trajectory.is_draft = False
    trajectory.save()
    
    TrajectoryCourse.objects.filter(trajectory=trajectory).delete()
    
    for course_data in courses_data:
        TrajectoryCourse.objects.create(
            trajectory=trajectory,
            course_id=course_data['course_id'],
            semester=course_data['semester'],
            position=course_data['position'],
            order=course_data['order']
        )
    
    return JsonResponse({'success': True, 'trajectory_id': trajectory.id})

@login_required
def create_trajectory_draft(request):
    trajectory = Trajectory.objects.create(
        student=request.user,
        name='Новая траектория',
        trajectory_type='personal',
        is_draft=True
    )
    
    return redirect('trajectory_editor', trajectory_id=trajectory.id)

@login_required
def course_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
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
    
    if trajectory.student != request.user and not request.user.is_staff:
        return HttpResponseForbidden("Вы не можете удалить эту траекторию")
    
    if request.method == 'POST':
        trajectory.delete()
        return redirect('trajectory_list')
    
    return redirect('trajectory_list')