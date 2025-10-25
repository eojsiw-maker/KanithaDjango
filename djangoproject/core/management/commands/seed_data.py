from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from core.models import Faculty, Department, Course, Student, Registration

class Command(BaseCommand):
    help = 'Seed database with Faculty of Science (KPRU) data: faculties, departments, courses, students, registrations'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Faculty
            faculty_name = 'คณะวิทยาศาสตร์ (มหาวิทยาลัยราชภัฏกำแพงเพชร)'
            fac, created = Faculty.objects.get_or_create(code='SCI', name=faculty_name)
            self.stdout.write(self.style.SUCCESS(f"Faculty: {fac.name} ({'created' if created else 'exists'})"))

            # Departments (code, name)
            depts = [
                ('MATH', 'คณิตศาสตร์'),
                ('STAT', 'สถิติ'),
                ('CS', 'วิทยาการคอมพิวเตอร์'),
                ('IT', 'เทคโนโลยีสารสนเทศ'),
                ('PHYS', 'ฟิสิกส์'),
                ('CHEM', 'เคมี'),
                ('BIO', 'ชีววิทยา'),
            ]
            dept_objs = {}
            for code, name in depts:
                d, d_created = Department.objects.get_or_create(code=code, name=name, faculty=fac)
                dept_objs[code] = d
                self.stdout.write(self.style.SUCCESS(f"Department: {d.name} ({'created' if d_created else 'exists'})"))

            # Courses per department: (code, name, units, dept_code)
            courses = [
                ('MATH101', 'แคลคูลัสเบื้องต้น', 3, 'MATH'),
                ('MATH201', 'พีชคณิตเชิงเส้น', 3, 'MATH'),
                ('STAT101', 'สถิติพื้นฐาน', 3, 'STAT'),
                ('CS101', 'แนะนำการเขียนโปรแกรม', 3, 'CS'),
                ('CS201', 'โครงสร้างข้อมูล', 3, 'CS'),
                ('IT101', 'เครือข่ายคอมพิวเตอร์เบื้องต้น', 3, 'IT'),
                ('PHYS101', 'ฟิสิกส์ทั่วไป 1', 3, 'PHYS'),
                ('CHEM101', 'เคมีทั่วไป 1', 3, 'CHEM'),
                ('BIO101', 'ชีววิทยาทั่วไป 1', 3, 'BIO'),
            ]
            for code, name, units, dept_code in courses:
                dept = dept_objs.get(dept_code)
                if not dept:
                    self.stdout.write(self.style.WARNING(f"Missing department for course {code}, skipping"))
                    continue
                c_obj, c_created = Course.objects.get_or_create(code=code, name=name, units=units, department=dept)
                self.stdout.write(self.style.SUCCESS(f"Course: {c_obj.code} - {c_obj.name} ({'created' if c_created else 'exists'})"))

            # Sample students (student_id, first_name, last_name, dept_code)
            students_data = [
                ('kpru1001', 'สมชาย', 'ทองดี', 'CS'),
                ('kpru1002', 'สุดา', 'ใจงาม', 'IT'),
                ('kpru1003', 'นิรันดร์', 'สุขสวัสดิ์', 'MATH'),
                ('kpru1004', 'วรินทร์', 'แสงทอง', 'PHYS'),
                ('kpru1005', 'กมล', 'นุ่มนวล', 'CHEM'),
            ]
            default_password = 'pass1234'
            for sid, fn, ln, dept_code in students_data:
                dept = dept_objs.get(dept_code)
                student, s_created = Student.objects.get_or_create(
                    student_id=sid,
                    defaults={'first_name': fn, 'last_name': ln, 'department': dept}
                )
                # create corresponding Django user if not exists
                if not User.objects.filter(username=sid).exists():
                    User.objects.create_user(username=sid, password=default_password, first_name=fn, last_name=ln)
                    self.stdout.write(self.style.SUCCESS(f"Created user {sid} with password {default_password}"))
                self.stdout.write(self.style.SUCCESS(f"Student: {student.student_id} - {student.first_name} ({'created' if s_created else 'exists'})"))

            # Create a superuser admin if not exists
            admin_username = 'admin'
            admin_password = 'adminpass'
            if not User.objects.filter(username=admin_username).exists():
                User.objects.create_superuser(username=admin_username, email='', password=admin_password)
                self.stdout.write(self.style.SUCCESS(f"Superuser created: {admin_username} / {admin_password}"))
            else:
                self.stdout.write(self.style.NOTICE(f"Superuser '{admin_username}' already exists"))

            # Sample registrations: assign some students to courses
            try:
                s1 = Student.objects.get(student_id='kpru1001')
                cs101 = Course.objects.get(code='CS101')
                Registration.objects.get_or_create(student=s1, course=cs101, year=2025, semester='1', defaults={'units': cs101.units, 'grade': 'A'})
                self.stdout.write(self.style.SUCCESS("Registration created: kpru1001 -> CS101"))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Skipping registration creation: {e}"))

            try:
                s2 = Student.objects.get(student_id='kpru1002')
                it101 = Course.objects.get(code='IT101')
                Registration.objects.get_or_create(student=s2, course=it101, year=2025, semester='1', defaults={'units': it101.units, 'grade': 'B'})
                self.stdout.write(self.style.SUCCESS("Registration created: kpru1002 -> IT101"))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Skipping registration creation: {e}"))

            self.stdout.write(self.style.SUCCESS("Seeding complete. Sample student credentials:"))
            for sid, _, _, _ in students_data:
                self.stdout.write(self.style.SUCCESS(f"  username={sid} password={default_password}"))
            self.stdout.write(self.style.SUCCESS(f"Admin: username={admin_username} password={admin_password}"))
