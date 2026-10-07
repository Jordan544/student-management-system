from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.utils import timezone
from .models import Student, TeacherProfile, SchoolEvent, GradeReport, Timetable
from .forms import StudentForm, SchoolEventForm, GradeReportForm, StudentWithdrawalForm
from .decorators import role_required
from django.contrib.auth import logout
import datetime


@login_required(login_url='login')
def dashboard_view(request):
    user = request.user
    is_admin = user.is_superuser or user.groups.filter(name='Admin').exists()
    is_teacher = user.groups.filter(name='Teacher').exists()
    
    can_add_students = is_admin
    if is_teacher:
        profile = getattr(user, 'teacher_profile', None)
        if profile and profile.can_add_students:
            can_add_students = True

    total_students = Student.objects.filter(is_active=True).count()
    total_teachers = User.objects.filter(groups__name='Teacher').count()
    
    teacher_registrations = []
    if is_admin:
        teacher_registrations = Student.objects.filter(added_by__groups__name='Teacher').order_by('-date_registered')[:5]

    upcoming_events = SchoolEvent.objects.filter(event_date__gte=timezone.now().date()).order_by('event_date')[:5]
    class_levels = Student.objects.filter(is_active=True).values_list('level', flat=True).distinct()

    all_timetables = Timetable.objects.all().order_by('day_of_week', 'start_time')
    
    if is_teacher:
        teacher_timetable = Timetable.objects.filter(teacher=user).order_by('day_of_week', 'start_time')
    else:
        teacher_timetable = Timetable.objects.none()

    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'is_admin': is_admin,
        'is_teacher': is_teacher,
        'can_add_students': can_add_students,
        'teacher_registrations': teacher_registrations,
        'upcoming_events': upcoming_events,
        'class_levels': class_levels,
        'teacher_timetable': teacher_timetable,
        'all_timetables': all_timetables,
    }
    return render(request, 'student_system/dashboard.html', context)

@login_required(login_url='login')
@role_required(allowed_roles=['Admin', 'Teacher'])
def student_list_view(request):
    user = request.user
    is_admin = user.is_superuser or user.groups.filter(name='Admin').exists()
    is_teacher = user.groups.filter(name='Teacher').exists()

    show_withdrawn = request.GET.get('status') == 'withdrawn'

    if is_admin:
        if show_withdrawn:
            students = Student.objects.filter(is_active=False).order_by('-withdrawal_date')
        else:
            students = Student.objects.filter(is_active=True).order_by('-date_registered')
    elif is_teacher:
        profile = getattr(user, 'teacher_profile', None)
        if profile and profile.allowed_levels:
            allowed_levels = [lvl.strip() for lvl in profile.allowed_levels.split(',')]
            students = Student.objects.filter(is_active=True, level__in=allowed_levels).order_by('-date_registered')
        else:
            students = Student.objects.none()
    else:
        students = Student.objects.none()

    query = request.GET.get('q', '')
    if query:
        students = students.filter(
            Q(name__icontains=query) | 
            Q(level__icontains=query) | 
            Q(student_number__icontains=query)
        )

    return render(request, 'student_system/student_list.html', {'students': students, 'query': query, 'show_withdrawn': show_withdrawn})

@login_required(login_url='login')
def register_student_view(request):
    if request.method == 'POST':
        # CRITICAL: request.FILES must be passed here to capture uploaded images
        form = StudentForm(request.POST, request.FILES) 
        if form.is_valid():
            student = form.save(commit=False)
            student.added_by = request.user
            student.save()
            return redirect('student_list')
        else:
            print("Form validation errors:", form.errors)
    else:
        form = StudentForm()
    
    return render(request, 'student_system/register.html', {'form': form})

@login_required(login_url='login')
@role_required(allowed_roles=['Admin'])
def withdraw_student_view(request, pk):
    student = get_object_or_404(Student, pk=pk)
    student.is_active = False
    student.withdrawal_date = timezone.now().date()
    student.save()
    return redirect('student_list')

@login_required(login_url='login')
@role_required(allowed_roles=['Admin'])
def add_teacher_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        allowed_levels = request.POST.get('allowed_levels')
        
        if username and password:
            user = User.objects.create_user(username=username, email=email, password=password)
            teacher_group = Group.objects.get(name='Teacher')
            user.groups.add(teacher_group)
            TeacherProfile.objects.create(user=user, allowed_levels=allowed_levels)
            return redirect('teacher_list')
            
    return render(request, 'student_system/teacher_form.html')

@login_required(login_url='login')
@role_required(allowed_roles=['Admin'])
def toggle_teacher_permission_view(request, user_id):
    profile, created = TeacherProfile.objects.get_or_create(user_id=user_id)
    profile.can_add_students = not profile.can_add_students
    profile.save()
    return redirect('teacher_list')

@login_required(login_url='login')
@role_required(allowed_roles=['Admin'])
def delete_teacher_view(request, pk):
    teacher = get_object_or_404(User, pk=pk)
    teacher.delete()
    return redirect('teacher_list')

@login_required(login_url='login')
@role_required(allowed_roles=['Admin'])
def teacher_list_view(request):
    teachers = User.objects.filter(groups__name='Teacher').order_by('username')
    return render(request, 'student_system/teacher_list.html', {'teachers': teachers})

@login_required(login_url='login')
@role_required(allowed_roles=['Admin', 'Teacher'])
def student_detail_view(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, 'student_system/student_detail.html', {'student': student})

def custom_logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def add_school_event(view_request):
    if not view_request.user.is_staff:
        return redirect('dashboard')
        
    if view_request.method == 'POST':
        form = SchoolEventForm(view_request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = SchoolEventForm()
        
    return render(view_request, 'student_system/add_event.html', {'form': form})

@login_required
def delete_school_event(view_request, event_id):
    if not view_request.user.is_staff:
        return redirect('dashboard')
        
    event = get_object_or_404(SchoolEvent, id=event_id)
    
    if view_request.method == 'POST':
        event.delete()
        return redirect('dashboard')
        
    return render(view_request, 'student_system/delete_event_confirm.html', {'event': event})

@login_required
def class_student_list(request, level_name):
    students = Student.objects.filter(level=level_name, is_active=True)
    return render(request, 'student_system/class_student_list.html', {
        'level_name': level_name,
        'students': students,
    })

@login_required
def withdraw_student(request, student_id):
    if not request.user.is_staff:
        return redirect('dashboard')
        
    student = get_object_or_404(Student, id=student_id)
    level_name = student.level
    
    if request.method == 'POST':
        form = StudentWithdrawalForm(request.POST, instance=student)
        if form.is_valid():
            student = form.save(commit=False)
            student.is_active = False
            student.save()
            return redirect('class_student_list', level_name=level_name)
    else:
        form = StudentWithdrawalForm(instance=student)
        
    return render(request, 'student_system/withdraw_student.html', {'form': form, 'student': student, 'level_name': level_name})