from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from student_system.models import Student

class Command(BaseCommand):
    help = 'Initializes Admin, Teacher, and Student user groups and permissions.'

    def handle(self, *args, **kwargs):
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        teacher_group, _ = Group.objects.get_or_create(name='Teacher')
        student_group, _ = Group.objects.get_or_create(name='Student')

        student_content_type = ContentType.objects.get_for_model(Student)
        student_permissions = Permission.objects.filter(content_type=student_content_type)

        # Admin gets all permissions
        for perm in student_permissions:
            admin_group.permissions.add(perm)

        # Teacher gets view-only permissions for directory lists
        for perm in student_permissions:
            if perm.codename.startswith('view_'):
                teacher_group.permissions.add(perm)

        self.stdout.write(self.style.SUCCESS('Successfully configured Admin, Teacher, and Student groups!'))