from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='student_system/login.html'), name='login'),
    path('logout/', views.custom_logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Student Routes
    path('register/', views.register_student_view, name='register_student'),
    path('students/', views.student_list_view, name='student_list'),
    path('student/<int:pk>/', views.student_detail_view, name='student_detail'),
    
    # Teacher Management Routes (Admin Only)
    path('teachers/', views.teacher_list_view, name='teacher_list'),
    path('teachers/add/', views.add_teacher_view, name='add_teacher'),
    path('teachers/delete/<int:pk>/', views.delete_teacher_view, name='delete_teacher'),
    path('teachers/toggle-permission/<int:user_id>/', views.toggle_teacher_permission_view, name='toggle_teacher_permission'),

    # School Event Routes
    path('events/add/', views.add_school_event, name='add_school_event'),
    path('events/delete/<int:event_id>/', views.delete_school_event, name='delete_school_event'),

    #class
    path('class/<str:level_name>/', views.class_student_list, name='class_student_list'),
    path('student/withdraw/<int:student_id>/', views.withdraw_student, name='withdraw_student'),

]