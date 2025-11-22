from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('courses/', views.courses_view, name='courses'),
    path('course/<int:course_id>/', views.course_view, name='course'),
    
    path('trajectory/', views.trajectory_view, name='trajectory_list'),
    path('trajectory/<int:trajectory_id>/', views.trajectory_view, name='trajectory'),
    path('trajectory/<int:trajectory_id>/delete/', views.delete_trajectory, name='delete_trajectory'),
    
    path('trajectory/create/', views.create_trajectory_draft, name='create_trajectory'),
    path('trajectory/editor/', views.trajectory_editor_view, name='trajectory_editor'),
    path('trajectory/editor/<int:trajectory_id>/', views.trajectory_editor_view, name='trajectory_editor'),
    path('trajectory/save/', views.save_trajectory, name='save_trajectory'),
    
    path('api/courses/', views.api_courses, name='api_courses'),
]