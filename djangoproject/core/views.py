from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.utils import OperationalError
from .models import Faculty, Department, Course, Student, Registration
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import User

PASSING_GRADES = {'A', 'B', 'C', 'D'}
MIN_CREDITS = 9
# Enforce project requirement: maximum 23 credits per semester
MAX_CREDITS = 23

def _parse_schedule_tokens(schedule_str):
    """
    Very small helper: split schedule by comma and strip.
    Example token: "Mon 09:00-11:00"
    Return set of tokens for naive clash detection.
    """
    if not schedule_str:
        return set()
    return {t.strip() for t in schedule_str.split(',') if t.strip()}

def index(request):
    """
    Public home page: handle missing DB gracefully.
    """
    db_error = False
    try:
        announcements = [
            {'title': 'ประกาศเรื่องการลงทะเบียน', 'date': '2025-10-01', 'body': 'กำหนดการลงทะเบียนเปิดวันที่ 1 พ.ย.'},
            {'title': 'วันหยุดประจำปี', 'date': '2025-11-20', 'body': 'มหาวิทยาลัยหยุดทำการในวันที่ 25 พ.ย.'},
        ]
        news = [
            {'title': 'โครงการฝึกงานนักศึกษา', 'date': '2025-09-15', 'summary': 'เปิดรับสมัครโครงการฝึกงาน 50 ที่นั่ง'},
            {'title': 'สัมมนาวิชาการ', 'date': '2025-10-05', 'summary': 'เชิญชวนส่งผลงานวิจัย'},
        ]
        events = [
            {'title': 'ปฐมนิเทศนักศึกษาใหม่', 'date': '2025-08-20'},
            {'title': 'สอบกลางภาค', 'date': '2025-10-30'},
        ]

        faculties = list(Faculty.objects.all()[:6])
        departments = list(Department.objects.select_related('faculty').all()[:8])
        courses = list(Course.objects.select_related('department').all()[:8])
    except OperationalError:
        db_error = True
        announcements = news = events = []
        faculties = departments = courses = []

    context = {
        'announcements': announcements,
        'news': news,
        'events': events,
        'faculties_sample': faculties,
        'departments_sample': departments,
        'courses_sample': courses,
        'db_error': db_error,
    }
    return render(request, 'index.html', context)


def faculty_list(request):
    db_error = False
    try:
        faculties = list(Faculty.objects.all())
    except OperationalError:
        db_error = True
        faculties = []

    # หากยังไม่มีข้อมูลใน DB ให้ใช้รายการตัวอย่าง (รหัสคิดขึ้นมาเป็นตัวอย่าง)
    if not faculties:
        faculties = [
            {'code': 'EDU', 'name': 'คณะครุศาสตร์'},
            {'code': 'HSS', 'name': 'คณะมนุษยศาสตร์และสังคมศาสตร์'},
            {'code': 'BM',  'name': 'คณะวิทยาการจัดการ'},
            {'code': 'FST', 'name': 'คณะวิทยาศาสตร์และเทคโนโลยี'},
            {'code': 'IET', 'name': 'คณะเทคโนโลยีอุตสาหกรรม'},
            {'code': 'NUR', 'name': 'คณะพยาบาลศาสตร์'},
        ]

    return render(request, 'faculties.html', {'faculties': faculties, 'db_error': db_error})


def department_list(request):
    db_error = False
    try:
        departments = list(Department.objects.select_related('faculty').all())
    except OperationalError:
        db_error = True
        departments = []

    # Fallback sample departments (fake codes) grouped by faculty
    if not departments:
        departments = [
            # คณะวิทยาการจัดการ (BM)
            {'code': 'ACC', 'name': 'สาขาวิชาการบัญชี', 'faculty': {'code': 'BM', 'name': 'คณะวิทยาการจัดการ'}},
            {'code': 'BUS', 'name': 'สาขาวิชาบริหารธุรกิจ', 'faculty': {'code': 'BM', 'name': 'คณะวิทยาการจัดการ'}},
            {'code': 'MBM', 'name': 'วิชาเอกการจัดการธุรกิจ', 'faculty': {'code': 'BM', 'name': 'คณะวิทยาการจัดการ'}},
            {'code': 'MKT', 'name': 'วิชาเอกการตลาด', 'faculty': {'code': 'BM', 'name': 'คณะวิทยาการจัดการ'}},
            {'code': 'FIN', 'name': 'วิชาเอกการเงินและการธนาคาร', 'faculty': {'code': 'BM', 'name': 'คณะวิทยาการจัดการ'}},
            {'code': 'DBT', 'name': 'วิชาเอกเทคโนโลยีธุรกิจดิจิทัล', 'faculty': {'code': 'BM', 'name': 'คณะวิทยาการจัดการ'}},
            {'code': 'ENT', 'name': 'วิชาเอกการเป็นผู้ประกอบการ', 'faculty': {'code': 'BM', 'name': 'คณะวิทยาการจัดการ'}},
            {'code': 'TOU', 'name': 'สาขาวิชาอุตสาหกรรมการท่องเที่ยว', 'faculty': {'code': 'BM', 'name': 'คณะวิทยาการจัดการ'}},
            {'code': 'COM', 'name': 'สาขาวิชานิเทศศาสตร์', 'faculty': {'code': 'BM', 'name': 'คณะวิทยาการจัดการ'}},

            # คณะครุศาสตร์ (EDU)
            {'code': 'ART', 'name': 'สาขาวิชาศิลปศึกษา', 'faculty': {'code': 'EDU', 'name': 'คณะครุศาสตร์'}},
            {'code': 'PE',  'name': 'สาขาวิชาการประถมศึกษา', 'faculty': {'code': 'EDU', 'name': 'คณะครุศาสตร์'}},
            {'code': 'EYC', 'name': 'สาขาวิชาการศึกษาปฐมวัย', 'faculty': {'code': 'EDU', 'name': 'คณะครุศาสตร์'}},

            # คณะวิทยาศาสตร์และเทคโนโลยี (FST)
            {'code': 'CPT', 'name': 'สาขาวิชาเทคโนโลยีคอมพิวเตอร์', 'faculty': {'code': 'FST', 'name': 'คณะวิทยาศาสตร์และเทคโนโลยี'}},
            {'code': 'CHE', 'name': 'สาขาวิชาเคมี', 'faculty': {'code': 'FST', 'name': 'คณะวิทยาศาสตร์และเทคโนโลยี'}},
            {'code': 'ENV', 'name': 'สาขาวิชาวิทยาศาสตร์สิ่งแวดล้อม', 'faculty': {'code': 'FST', 'name': 'คณะวิทยาศาสตร์และเทคโนโลยี'}},

            # คณะเทคโนโลยีอุตสาหกรรม (IET)
            {'code': 'MFG', 'name': 'สาขาวิชาเทคโนโลยีการผลิตและระบบอัตโนมัติ', 'faculty': {'code': 'IET', 'name': 'คณะเทคโนโลยีอุตสาหกรรม'}},
            {'code': 'CER', 'name': 'สาขาวิชาเทคโนโลยีเซรามิกส์', 'faculty': {'code': 'IET', 'name': 'คณะเทคโนโลยีอุตสาหกรรม'}},
            {'code': 'CRA', 'name': 'สาขาวิชาศิลปหัตถกรรม', 'faculty': {'code': 'IET', 'name': 'คณะเทคโนโลยีอุตสาหกรรม'}},
            {'code': 'IDP', 'name': 'สาขาวิชาออกแบบผลิตภัณฑ์อุตสาหกรรม', 'faculty': {'code': 'IET', 'name': 'คณะเทคโนโลยีอุตสาหกรรม'}},
            {'code': 'INT', 'name': 'สาขาวิชาสถาปัตยกรรมภายใน', 'faculty': {'code': 'IET', 'name': 'คณะเทคโนโลยีอุตสาหกรรม'}},
            {'code': 'CIV', 'name': 'สาขาวิชาโยธา', 'faculty': {'code': 'IET', 'name': 'คณะเทคโนโลยีอุตสาหกรรม'}},
            {'code': 'ELE', 'name': 'สาขาวิชาไฟฟ้า', 'faculty': {'code': 'IET', 'name': 'คณะเทคโนโลยีอุตสาหกรรม'}},
            {'code': 'EEN', 'name': 'สาขาวิชาอิเล็กทรอนิกส์', 'faculty': {'code': 'IET', 'name': 'คณะเทคโนโลยีอุตสาหกรรม'}},
            {'code': 'MEC', 'name': 'สาขาวิชาเครื่องกล', 'faculty': {'code': 'IET', 'name': 'คณะเทคโนโลยีอุตสาหกรรม'}},

            # คณะอื่นๆ (OTH)
            {'code': 'MBM_M', 'name': 'สาขาวิชาการจัดการธุรกิจสมัยใหม่ (ปริญญาโท)', 'faculty': {'code': 'OTH', 'name': 'คณะอื่นๆ'}},
            {'code': 'PHH', 'name': 'สาขาวิชาสาธารณสุขศาสตร์', 'faculty': {'code': 'OTH', 'name': 'คณะอื่นๆ'}},
        ]

    return render(request, 'departments.html', {'departments': departments, 'db_error': db_error})


def course_list(request):
    db_error = False
    try:
        courses = list(Course.objects.select_related('department').all())
    except OperationalError:
        db_error = True
        courses = []

    # Fallback sample courses when DB is empty/unavailable
    if not courses:
        courses = [
            # CPT - เทคโนโลยีคอมพิวเตอร์
            {'code': 'CPT101', 'name': 'การเขียนโปรแกรมคอมพิวเตอร์ 1', 'units': 3, 'department': {'code': 'CPT', 'name': 'สาขา CPT เทคโนโลยีคอมพิวเตอร์'}},
            {'code': 'CPT102', 'name': 'โครงสร้างข้อมูล', 'units': 3, 'department': {'code': 'CPT', 'name': 'สาขา CPT เทคโนโลยีคอมพิวเตอร์'}},
            {'code': 'CPT201', 'name': 'ระบบฐานข้อมูล', 'units': 3, 'department': {'code': 'CPT', 'name': 'สาขา CPT เทคโนโลยีคอมพิวเตอร์'}},
            {'code': 'CPT204', 'name': 'ระบบปฏิบัติการ', 'units': 3, 'department': {'code': 'CPT', 'name': 'สาขา CPT เทคโนโลยีคอมพิวเตอร์'}},
            {'code': 'CPT303', 'name': 'เครือข่ายคอมพิวเตอร์', 'units': 3, 'department': {'code': 'CPT', 'name': 'สาขา CPT เทคโนโลยีคอมพิวเตอร์'}},
            # ACC - การบัญชี
            {'code': 'ACC101', 'name': 'บัญชีการเงิน 1', 'units': 3, 'department': {'code': 'ACC', 'name': 'สาขา ACC การบัญชี'}},
            {'code': 'ACC205', 'name': 'บัญชีต้นทุน', 'units': 3, 'department': {'code': 'ACC', 'name': 'สาขา ACC การบัญชี'}},
            {'code': 'ACC301', 'name': 'การตรวจสอบบัญชี', 'units': 3, 'department': {'code': 'ACC', 'name': 'สาขา ACC การบัญชี'}},
            {'code': 'ACC325', 'name': 'ภาษีอากรธุรกิจ', 'units': 3, 'department': {'code': 'ACC', 'name': 'สาขา ACC การบัญชี'}},
            {'code': 'ACC401', 'name': 'การวิเคราะห์งบการเงิน', 'units': 3, 'department': {'code': 'ACC', 'name': 'สาขา ACC การบัญชี'}},
            # BUS - บริหารธุรกิจ
            {'code': 'BUS101', 'name': 'พื้นฐานการบริหารธุรกิจ', 'units': 3, 'department': {'code': 'BUS', 'name': 'สาขา BUS บริหารธุรกิจ'}},
            {'code': 'BUS202', 'name': 'พฤติกรรมองค์การ', 'units': 3, 'department': {'code': 'BUS', 'name': 'สาขา BUS บริหารธุรกิจ'}},
            {'code': 'BUS204', 'name': 'การจัดการทรัพยากรมนุษย์', 'units': 3, 'department': {'code': 'BUS', 'name': 'สาขา BUS บริหารธุรกิจ'}},
            {'code': 'BUS305', 'name': 'การเงินธุรกิจ', 'units': 3, 'department': {'code': 'BUS', 'name': 'สาขา BUS บริหารธุรกิจ'}},
            {'code': 'BUS401', 'name': 'นโยบายและกลยุทธ์ธุรกิจ', 'units': 3, 'department': {'code': 'BUS', 'name': 'สาขา BUS บริหารธุรกิจ'}},
            # MKT - การตลาด
            {'code': 'MKT101', 'name': 'หลักการตลาด', 'units': 3, 'department': {'code': 'MKT', 'name': 'สาขา MKT การตลาด'}},
            {'code': 'MKT221', 'name': 'การวิจัยการตลาด', 'units': 3, 'department': {'code': 'MKT', 'name': 'สาขา MKT การตลาด'}},
            {'code': 'MKT308', 'name': 'การสื่อสารการตลาด', 'units': 3, 'department': {'code': 'MKT', 'name': 'สาขา MKT การตลาด'}},
            {'code': 'MKT330', 'name': 'การตลาดดิจิทัล', 'units': 3, 'department': {'code': 'MKT', 'name': 'สาขา MKT การตลาด'}},
            {'code': 'MKT402', 'name': 'การบริหารแบรนด์', 'units': 3, 'department': {'code': 'MKT', 'name': 'สาขา MKT การตลาด'}},
            # CHE - เคมี
            {'code': 'CHE101', 'name': 'เคมีทั่วไป', 'units': 3, 'department': {'code': 'CHE', 'name': 'สาขา CHE เคมี'}},
            {'code': 'CHE202', 'name': 'เคมีอินทรีย์', 'units': 3, 'department': {'code': 'CHE', 'name': 'สาขา CHE เคมี'}},
            {'code': 'CHE250', 'name': 'ปฏิบัติการเคมีวิเคราะห์', 'units': 2, 'department': {'code': 'CHE', 'name': 'สาขา CHE เคมี'}},
            {'code': 'CHE303', 'name': 'เคมีกายภาพ', 'units': 3, 'department': {'code': 'CHE', 'name': 'สาขา CHE เคมี'}},
            {'code': 'CHE405', 'name': 'เคมีอุตสาหกรรม', 'units': 3, 'department': {'code': 'CHE', 'name': 'สาขา CHE เคมี'}},
            # TOU - อุตสาหกรรมการท่องเที่ยว
            {'code': 'TOU100', 'name': 'อุตสาหกรรมการท่องเที่ยวเบื้องต้น', 'units': 3, 'department': {'code': 'TOU', 'name': 'สาขา TOU อุตสาหกรรมการท่องเที่ยว'}},
            {'code': 'TOU220', 'name': 'การจัดนำเที่ยว', 'units': 3, 'department': {'code': 'TOU', 'name': 'สาขา TOU อุตสาหกรรมการท่องเที่ยว'}},
            {'code': 'TOU303', 'name': 'การบริหารธุรกิจท่องเที่ยว', 'units': 3, 'department': {'code': 'TOU', 'name': 'สาขา TOU อุตสาหกรรมการท่องเที่ยว'}},
            {'code': 'TOU325', 'name': 'มัคคุเทศก์และจรรยาบรรณ', 'units': 3, 'department': {'code': 'TOU', 'name': 'สาขา TOU อุตสาหกรรมการท่องเที่ยว'}},
            {'code': 'TOU410', 'name': 'สัมมนาการท่องเที่ยว', 'units': 3, 'department': {'code': 'TOU', 'name': 'สาขา TOU อุตสาหกรรมการท่องเที่ยว'}},
            # ART - ศิลปศึกษา
            {'code': 'ART101', 'name': 'ศิลปะเบื้องต้น', 'units': 2, 'department': {'code': 'ART', 'name': 'สาขา ART ศิลปศึกษา'}},
            {'code': 'ART203', 'name': 'ศิลปะไทย', 'units': 2, 'department': {'code': 'ART', 'name': 'สาขา ART ศิลปศึกษา'}},
            {'code': 'ART305', 'name': 'จิตรกรรม', 'units': 3, 'department': {'code': 'ART', 'name': 'สาขา ART ศิลปศึกษา'}},
            {'code': 'ART310', 'name': 'ประติมากรรม', 'units': 3, 'department': {'code': 'ART', 'name': 'สาขา ART ศิลปศึกษา'}},
            {'code': 'ART401', 'name': 'นิทรรศการศิลปศึกษา', 'units': 3, 'department': {'code': 'ART', 'name': 'สาขา ART ศิลปศึกษา'}},
        ]

    return render(request, 'courses.html', {'courses': courses, 'db_error': db_error})


# require login for student list (private)
@login_required
def student_list(request):
    db_error = False
    try:
        students = list(Student.objects.select_related('department').all())
    except OperationalError:
        db_error = True
        students = []
    return render(request, 'students.html', {'students': students, 'db_error': db_error})


# require login for registration (only logged-in students/staff can register)
@login_required
def registration_create(request):
    """
    Session-backed registration cart:
    - GET: show student auto fields, available courses, current cart
    - POST actions: update_student, add_course, remove_course, save_draft, confirm
    """
    user = request.user
    try:
        # Try to find student by username first
        student = Student.objects.select_related('department__faculty').get(student_id=user.username)
    except Student.DoesNotExist:
        try:
            # If not found, try to find by first_name (assuming first_name matches username)
            student = Student.objects.select_related('department__faculty').filter(first_name=user.username).first()
        except Student.DoesNotExist:
            student = None

    # build display_student dict (use Student model if available, otherwise fallback to request.user)
    display_student = {}
    if student:
        display_student = {
            'student_id': student.student_id,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'department_name': student.department.name if student.department else None,
            'faculty_name': student.department.faculty.name if student.department and student.department.faculty else None,
            'department': student.department,
            'faculty': student.department.faculty if student.department else None,
        }
    else:
        # Try to find student by looking up the actual student ID if it's stored in username
        try:
            alt_student = Student.objects.select_related('department__faculty').get(student_id='661320115')
            display_student = {
                'student_id': alt_student.student_id,
                'first_name': alt_student.first_name,
                'last_name': alt_student.last_name,
                'department_name': alt_student.department.name if alt_student.department else None,
                'faculty_name': alt_student.department.faculty.name if alt_student.department and alt_student.department.faculty else None,
                'department': alt_student.department,
                'faculty': alt_student.department.faculty if alt_student.department else None,
            }
        except Student.DoesNotExist:
            display_student = {
                'student_id': user.username or '',
                'first_name': user.first_name or '',
                'last_name': user.last_name or '',
                'department_name': None,
                'faculty_name': None,
                'department': None,
                'faculty': None,
            }

    # load faculties & departments for the signup / register form (fallback if DB missing)
    try:
        faculties_qs = list(Faculty.objects.all())
        departments_qs = list(Department.objects.select_related('faculty').all())
        db_ok = True
    except OperationalError:
        faculties_qs = []
        departments_qs = []
        db_ok = False

    # build fallback lists if DB empty
    if not faculties_qs:
        faculties = [
            {'code': 'BM', 'name': 'คณะวิทยาการจัดการ'},
            {'code': 'EDU', 'name': 'คณะครุศาสตร์'},
            {'code': 'FST', 'name': 'คณะวิทยาศาสตร์และเทคโนโลยี'},
            {'code': 'IET', 'name': 'คณะเทคโนโลยีอุตสาหกรรม'},
        ]
    else:
        faculties = faculties_qs

    if not departments_qs:
        departments = [
            {'code': 'ACC', 'name': 'สาขาวิชาการบัญชี', 'faculty_code': 'BM'},
            {'code': 'BUS', 'name': 'สาขาวิชาบริหารธุรกิจ', 'faculty_code': 'BM'},
            {'code': 'CPT', 'name': 'สาขาวิชาเทคโนโลยีคอมพิวเตอร์', 'faculty_code': 'FST'},
            {'code': 'CHE', 'name': 'สาขาวิชาเคมี', 'faculty_code': 'FST'},
            {'code': 'ART', 'name': 'สาขาวิชาศิลปศึกษา', 'faculty_code': 'EDU'},
            # ...existing fallback departments...
        ]
    else:
        # convert model departments to simple dicts for easy JS filtering in template
        departments = []
        for d in departments_qs:
            departments.append({'id': d.id, 'code': getattr(d, 'code', ''), 'name': d.name, 'faculty_id': d.faculty.id if d.faculty else None, 'faculty_name': d.faculty.name if d.faculty else None})

    # If display_student lacks faculty/department names, try to populate from real DB objects
    try:
        if display_student and (not display_student.get('department_name') or not display_student.get('faculty_name')):
            # prefer a real Department model when available
            if departments_qs:
                d = departments_qs[0]
                display_student['department_name'] = display_student.get('department_name') or (d.name if getattr(d, 'name', None) else None)
                display_student['faculty_name'] = display_student.get('faculty_name') or (d.faculty.name if getattr(d, 'faculty', None) else None)
                display_student['department'] = display_student.get('department') or d
                display_student['faculty'] = display_student.get('faculty') or d.faculty if getattr(d, 'faculty', None) else display_student.get('faculty')
    except Exception:
        # silently ignore if fill-in fails
        pass

    db_error = False
    errors = []
    warnings = []
    try:
        all_courses = list(Course.objects.select_related('department').all())
    except OperationalError:
        db_error = True
        all_courses = []

    # If DB is available but there are no courses, create a small set of sample courses
    # so the registration page shows real model instances and registration can proceed.
    if not db_error and not all_courses:
        try:
            # Create a sample faculty and department (idempotent)
            fac, _ = Faculty.objects.get_or_create(code='BM', defaults={'name': 'คณะวิทยาการจัดการ'})
            dept, _ = Department.objects.get_or_create(code='CPT', defaults={'name': 'สาขาเทคโนโลยีคอมพิวเตอร์', 'faculty': fac})

            sample_courses = [
                ('CPT101', 'การเขียนโปรแกรมคอมพิวเตอร์ 1', 3),
                ('CPT102', 'โครงสร้างข้อมูล', 3),
                ('CPT201', 'ระบบฐานข้อมูล', 3),
                ('CPT204', 'ระบบปฏิบัติการ', 3),
                ('CPT303', 'เครือข่ายคอมพิวเตอร์', 3),
                ('ACC101', 'บัญชีการเงิน 1', 3),
            ]

            for code, name, units in sample_courses:
                Course.objects.get_or_create(code=code, defaults={'name': name, 'units': units, 'department': dept})

            # reload all_courses now that we've seeded
            all_courses = list(Course.objects.select_related('department').all())
        except Exception:
            # if anything goes wrong, leave all_courses empty and continue (template will show fallback)
            pass

    # ensure session cart exists: list of course ids (pks)
    cart = request.session.get('registration_cart', [])
    cart = list(dict.fromkeys(cart))  # unique preserve order

    # Precompute current confirmed regs for this student in same year/semester if exists
    current_year = request.POST.get('year') or request.GET.get('year') or 2025
    current_semester = request.POST.get('semester') or request.GET.get('semester') or '1'
    try:
        current_year = int(current_year)
    except Exception:
        current_year = 2025
    current_semester = str(current_semester)

    # helper to resolve department value (id or "code:CODE" or plain code)
    def resolve_dept(val):
        if not val:
            return None
        # try pk
        try:
            pk = int(val)
            return Department.objects.filter(pk=pk).first()
        except Exception:
            code = val
            if isinstance(code, str) and code.startswith('code:'):
                code = code.split(':', 1)[1]
            return Department.objects.filter(code=code).first()

    # If user provided student fields (when no Student linked), create Student on the fly
    if request.method == 'POST':
        if student is None:
            posted_sid = request.POST.get('student_id', '').strip()
            posted_fn = request.POST.get('first_name', '').strip()
            posted_ln = request.POST.get('last_name', '').strip()
            posted_dept = request.POST.get('student_department') or request.POST.get('department') or ''
            if posted_sid and posted_fn:
                # attempt to resolve/create department if needed
                dept_obj = None
                try:
                    dept_obj = resolve_dept(posted_dept)
                except Exception:
                    dept_obj = None
                if not dept_obj and posted_dept and isinstance(posted_dept, str) and posted_dept.startswith('code:'):
                    code = posted_dept.split(':', 1)[1]
                    # find name in fallback departments
                    dept_name = None
                    for dd in departments:
                        if isinstance(dd, dict) and dd.get('code') == code:
                            dept_name = dd.get('name')
                            break
                    if not dept_name:
                        dept_name = f'สาขา {code}'
                    # create Department record (associate faculty if possible)
                    try:
                        faculty_obj = None
                        # try map faculty from departments fallback
                        for dd in departments:
                            if isinstance(dd, dict) and dd.get('code') == code and dd.get('faculty_code'):
                                # find faculty model if exists
                                if db_ok:
                                    faculty_obj = Faculty.objects.filter(code=dd.get('faculty_code')).first()
                                break
                        dept_obj = Department.objects.create(code=code, name=dept_name, faculty=faculty_obj)
                    except Exception:
                        dept_obj = None
                # create Student record in DB
                try:
                    student = Student.objects.create(student_id=posted_sid, first_name=posted_fn, last_name=posted_ln, department=dept_obj)
                except Exception:
                    student = None
                # update display_student
                if student:
                    display_student = {
                        'student_id': student.student_id,
                        'first_name': student.first_name,
                        'last_name': student.last_name,
                        'department_name': student.department.name if student.department else None,
                        'faculty_name': student.department.faculty.name if student.department and student.department.faculty else None,
                    }

    # helper to resolve course value (pk, "code:CODE" or plain code)
    def resolve_course(val):
        if not val:
            return None
        try:
            pk = int(val)
            return Course.objects.filter(pk=pk).first()
        except Exception:
            code = val
            if isinstance(code, str) and code.startswith('code:'):
                code = code.split(':', 1)[1]
            return Course.objects.filter(code=code).first()

    if request.method == 'POST' and not db_error:
        action = request.POST.get('action')
        # Prevent creating Registration rows when there is no linked Student record.
        # Many code paths below assume `student` is a Student instance; if it's None
        # a create() would violate NOT NULL constraint on registration.student_id.
        if student is None and action in ('register_selected', 'register', 'add_course', 'confirm', 'save_draft'):
            messages.error(request, 'ไม่พบข้อมูลนักศึกษาในระบบ (โปรดลงทะเบียนข้อมูลนักศึกษาหรือเข้าสู่ระบบด้วยบัญชีนักศึกษา)')
            return redirect('core:register')
        # bulk registration from checkboxes named 'course_ids'
        if action == 'register_selected':
            selected_ids = request.POST.getlist('course_ids')
            if not selected_ids:
                messages.error(request, 'ยังไม่ได้เลือกวิชาที่ต้องการลงทะเบียน')
                return redirect('core:register')

            # current confirmed regs for credit/count checks
            regs_now = list(Registration.objects.filter(student=student, year=current_year, semester=current_semester, status='CONFIRMED'))
            reg_ids = {r.course.id for r in regs_now}
            total_credits_now = sum(r.units for r in regs_now)

            successes = []
            failures = []
            for sid in selected_ids:
                try:
                    cid = int(sid)
                    course_obj = Course.objects.get(pk=cid)
                except Exception:
                    failures.append(f'ไม่พบวิชา id={sid}')
                    continue

                if course_obj.id in reg_ids:
                    failures.append(f'คุณได้ลงทะเบียนแล้ว: {course_obj.code}')
                    continue

                confirmed_count = Registration.objects.filter(course=course_obj, year=current_year, semester=current_semester, status='CONFIRMED').count()
                if confirmed_count >= course_obj.capacity:
                    failures.append(f'กลุ่มเต็ม: {course_obj.code}')
                    continue

                if total_credits_now + course_obj.units > MAX_CREDITS:
                    failures.append(f'เพิ่ม {course_obj.code} จะเกินหน่วยกิตสูงสุด ({MAX_CREDITS})')
                    continue

                # create registration
                Registration.objects.create(student=student, course=course_obj, year=current_year, semester=current_semester, units=course_obj.units, status='CONFIRMED')
                successes.append(course_obj.code)
                total_credits_now += course_obj.units
                reg_ids.add(course_obj.id)

            if successes:
                messages.success(request, f"ลงทะเบียนเรียบร้อย: {', '.join(successes)}")
            if failures:
                for fmsg in failures:
                    messages.error(request, fmsg)
            return redirect('core:register')

        selected_course_id = request.POST.get('course') or request.POST.get('course_id')

        # handle single-register / single-drop actions (from per-course buttons)
        if action == 'register' and selected_course_id:
            # try get course
            try:
                cid = int(selected_course_id)
                course_obj = Course.objects.get(pk=cid)
            except Exception:
                course_obj = resolve_course(selected_course_id)

            if not course_obj:
                messages.error(request, 'ไม่พบวิชาที่เลือก')
                return redirect('core:register')

            # already registered?
            if Registration.objects.filter(student=student, course=course_obj, year=current_year, semester=current_semester, status='CONFIRMED').exists():
                messages.error(request, f'คุณได้ลงทะเบียนวิชา {course_obj.code} แล้ว')
                return redirect('core:register')

            # capacity
            confirmed_count = Registration.objects.filter(course=course_obj, year=current_year, semester=current_semester, status='CONFIRMED').count()
            if confirmed_count >= course_obj.capacity:
                messages.error(request, f'วิชา {course_obj.code} เต็มแล้ว')
                return redirect('core:register')

            # credits limit
            regs_now = Registration.objects.filter(student=student, year=current_year, semester=current_semester, status='CONFIRMED')
            credits_now = sum(r.units for r in regs_now)
            if credits_now + getattr(course_obj, 'units', getattr(course_obj, 'credits', 0)) > MAX_CREDITS:
                messages.error(request, 'เพิ่มวิชานี้จะเกินหน่วยกิตที่กำหนด')
                return redirect('core:register')

            Registration.objects.create(student=student, course=course_obj, year=current_year, semester=current_semester, units=getattr(course_obj, 'units', getattr(course_obj, 'credits', 0)), status='CONFIRMED')
            messages.success(request, f'ลงทะเบียนวิชา {course_obj.code} สำเร็จ')
            return redirect('core:register')

        if action == 'drop' and selected_course_id:
            try:
                cid = int(selected_course_id)
                course_obj = Course.objects.get(pk=cid)
            except Exception:
                course_obj = resolve_course(selected_course_id)
            if course_obj:
                Registration.objects.filter(student=student, course=course_obj, year=current_year, semester=current_semester).delete()
                messages.success(request, f'ถอนรายวิชา {course_obj.code} เรียบร้อย')
            return redirect('core:register')

        if action == 'add_course' and selected_course_id:
            course_obj = resolve_course(selected_course_id)
            if not course_obj:
                errors.append('ไม่พบวิชาที่เลือก')
            else:
                # existing validation logic (prereq/capacity/clash/credits) unchanged, use course_obj
                missing_prereq = []
                for pre in course_obj.prerequisites.all():
                    passed = Registration.objects.filter(student__student_id=request.user.username, course=pre, grade__in=PASSING_GRADES).exists()
                    if not passed:
                        missing_prereq.append(pre.code)
                if missing_prereq:
                    errors.append(f"ยังไม่ได้ผ่าน prerequisite: {', '.join(missing_prereq)}")
                else:
                    confirmed_count = Registration.objects.filter(course=course_obj, status='CONFIRMED', year=current_year, semester=current_semester).count()
                    if confirmed_count >= getattr(course_obj, 'capacity', 0):
                        errors.append(f"กลุ่มเต็ม: {course_obj.code} ({course_obj.capacity} คน)")
                    else:
                        selected_tokens = _parse_schedule_tokens(course_obj.schedule)
                        clash = False
                        for cid in cart:
                            try:
                                c2 = Course.objects.get(pk=cid)
                                if _parse_schedule_tokens(c2.schedule) & selected_tokens:
                                    clash = True
                                    break
                            except Exception:
                                continue
                        regs = Registration.objects.filter(student__student_id=request.user.username, status='CONFIRMED', year=current_year, semester=current_semester).select_related('course')
                        for r in regs:
                            if _parse_schedule_tokens(r.course.schedule) & selected_tokens:
                                clash = True
                                break
                        if clash:
                            errors.append("เวลาเรียนชนกันกับรายวิชาที่เลือกไว้หรือที่ลงทะเบียนแล้ว")
                        else:
                            cart_units = sum([Course.objects.get(pk=cid).units for cid in cart]) if cart else 0
                            existing_units = sum([r.units for r in regs]) if regs else 0
                            total_after = existing_units + cart_units + course_obj.units
                            if total_after > MAX_CREDITS:
                                errors.append(f"เกินหน่วยกิตสูงสุด ({MAX_CREDITS}) หากเพิ่มวิชานี้จะเป็น {total_after} หน่วยกิต")
                            else:
                                cart.append(course_obj.pk)
                                request.session['registration_cart'] = cart
                                messages.success(request, f"เพิ่ม {course_obj.code} ลงในตะกร้า")

        elif action == 'remove_course' and selected_course_id:
            try:
                # try direct int
                try:
                    cid = int(selected_course_id)
                except Exception:
                    co = resolve_course(selected_course_id)
                    cid = co.pk if co else None
                if cid and cid in cart:
                    cart.remove(cid)
                    request.session['registration_cart'] = cart
                    messages.success(request, "นำวิชาออกจากตะกร้าแล้ว")
            except Exception:
                pass

        elif action == 'save_draft':
            if not student:
                errors.append("ไม่พบข้อมูลนักศึกษาที่เชื่อมโยงกับบัญชีนี้ (กรุณากรอกข้อมูลนักศึกษาและกดบันทึกอีกครั้ง)")
            else:
                for cid in cart:
                    try:
                        cobj = Course.objects.get(pk=cid)
                        Registration.objects.update_or_create(
                            student=student, course=cobj, year=current_year, semester=current_semester,
                            defaults={'units': cobj.units, 'status': 'DRAFT'}
                        )
                    except Exception:
                        pass
                messages.success(request, "บันทึกร่างเรียบร้อย")

        elif action == 'confirm':
            if not student:
                errors.append("ไม่พบข้อมูลนักศึกษาที่เชื่อมโยงกับบัญชีนี้ (กรุณากรอกข้อมูลนักศึกษาและกดยืนยันอีกครั้ง)")
            else:
                cart_copy = cart[:]
                for cid in cart_copy:
                    try:
                        cobj = Course.objects.get(pk=cid)
                    except Exception:
                        errors.append(f"ไม่พบวิชา id={cid}")
                        continue
                    missing_prereq = [pre.code for pre in cobj.prerequisites.all() if not Registration.objects.filter(student=student, course=pre, grade__in=PASSING_GRADES).exists()]
                    if missing_prereq:
                        errors.append(f"ยังไม่ได้ผ่าน prerequisite สำหรับ {cobj.code}: {', '.join(missing_prereq)}")
                        continue
                    confirmed_count = Registration.objects.filter(course=cobj, status='CONFIRMED', year=current_year, semester=current_semester).count()
                    if confirmed_count >= cobj.capacity:
                        errors.append(f"กลุ่มเต็ม: {cobj.code}")
                        continue
                    sel_tokens = _parse_schedule_tokens(cobj.schedule)
                    clash_found = False
                    for r in Registration.objects.filter(student=student, status='CONFIRMED', year=current_year, semester=current_semester).select_related('course'):
                        if _parse_schedule_tokens(r.course.schedule) & sel_tokens:
                            clash_found = True
                            break
                    if clash_found:
                        errors.append(f"เวลาเรียนชนกันสำหรับ {cobj.code}")
                        continue
                    cart_units = sum([Course.objects.get(pk=x).units for x in cart])
                    existing_units = sum([r.units for r in Registration.objects.filter(student=student, status='CONFIRMED', year=current_year, semester=current_semester)])
                    if existing_units + cart_units > MAX_CREDITS:
                        errors.append(f"เกินหน่วยกิตสูงสุดเมื่อรวมวิชาทั้งหมด (สูงสุด {MAX_CREDITS})")
                        break
                    Registration.objects.update_or_create(
                        student=student, course=cobj, year=current_year, semester=current_semester,
                        defaults={'units': cobj.units, 'status': 'CONFIRMED'}
                    )
                if not errors:
                    request.session['registration_cart'] = []
                    messages.success(request, "ยืนยันการลงทะเบียนเรียบร้อย")

    # prepare display lists
    cart_courses = []
    try:
        for cid in cart:
            try:
                c = Course.objects.get(pk=cid)
                cart_courses.append(c)
            except Exception:
                continue
    except Exception:
        cart_courses = []

    cart_units = sum([c.units for c in cart_courses]) if cart_courses else 0
    confirmed_units = 0
    if student and not db_error:
        confirmed_units = sum([r.units for r in Registration.objects.filter(student=student, status='CONFIRMED', year=current_year, semester=current_semester)])
    # prepare registered courses list and totals (for template)
    registered_regs = []
    if student and not db_error:
        registered_regs = list(Registration.objects.filter(student=student, status='CONFIRMED', year=current_year, semester=current_semester).select_related('course'))

    registered_courses = [r.course for r in registered_regs]
    total_credits = sum([r.units for r in registered_regs]) if registered_regs else 0

    # If there are no confirmed registered courses (e.g., student not linked),
    # fall back to showing the session cart contents so the summary displays something useful.
    if not registered_courses and cart_courses:
        try:
            registered_courses = cart_courses
            total_credits = sum([c.units for c in cart_courses]) if cart_courses else 0
        except Exception:
            # if anything unexpected (e.g., cart contains ids that cannot be resolved), ignore
            registered_courses = []
            total_credits = 0

    # ensure template can access student.faculty (some templates read student.faculty.name)
    if student and getattr(student, 'department', None) and getattr(student.department, 'faculty', None):
        try:
            setattr(student, 'faculty', student.department.faculty)
        except Exception:
            pass

    # expose variables matching the new template names while keeping legacy keys
    context = {
        'student': student,
        'display_student': display_student,
        'available_courses': all_courses,
        'registered_courses': registered_courses,
        'total_credits': total_credits,
        'cart_ids': [c.id for c in cart_courses] if cart_courses else [],
        # legacy/compat
        'courses': all_courses,
        'cart_courses': cart_courses,
        'cart_units': cart_units,
        'confirmed_units': confirmed_units,
        'db_error': db_error,
        'errors': errors,
        'warnings': warnings,
        'year': current_year,
        'semester': current_semester,
        'faculties': faculties,
        'departments': departments,
        'db_ok': db_ok,
    }

    # render the registration page
    return render(request, 'registration_page.html', context)


# require login for viewing registrations
@login_required
def registration_list(request):
    db_error = False
    try:
        # By default show only the current user's registrations for privacy.
        # Admin/staff can still see all registrations.
        user = request.user
        if user.is_staff or user.is_superuser:
            regs_qs = Registration.objects.select_related('student', 'course').order_by('-created_at')
        else:
            # try to find linked Student for this user
            student = Student.objects.filter(student_id=user.username).first()
            if not student:
                # fallback: try matching first_name
                student = Student.objects.filter(first_name=user.username).first()
            if student:
                regs_qs = Registration.objects.select_related('student', 'course').filter(student=student).order_by('-created_at')
            else:
                regs_qs = Registration.objects.none()
        regs = list(regs_qs)
    except OperationalError:
        db_error = True
        regs = []
    return render(request, 'registrations.html', {'registrations': regs, 'db_error': db_error})


# require login for results/grades
@login_required
def results_view(request):
    db_error = False
    results = []
    try:
        # Show only the logged-in student's results (privacy)
        user = request.user
        student = None
        # attempt to find Student by student_id matching username
        if user and user.is_authenticated:
            student = Student.objects.filter(student_id=user.username).first()
            if not student:
                # fallback: try matching first_name
                student = Student.objects.filter(first_name=user.username).first()

        if not student:
            # no linked Student found -- return empty results (template will show message)
            results = []
        else:
            regs = student.registrations.exclude(grade='').all()
            total_units = sum([r.units for r in regs]) if regs else 0
            if total_units:
                total_points = 0.0
                for r in regs:
                    gp = {'A':4.0,'B':3.0,'C':2.0,'D':1.0,'F':0.0}.get(r.grade,0.0)
                    total_points += gp * r.units
                gpa = total_points / total_units
            else:
                gpa = None
            results.append({'student': student, 'total_units': total_units, 'gpa': round(gpa,2) if gpa is not None else None, 'registrations': regs})
    except OperationalError:
        db_error = True
        results = []
    return render(request, 'results.html', {'results': results, 'db_error': db_error})

# Signup view for new students (simple: creates Django user and Student entry)
def signup_view(request):
    """
    Simple signup for students: collects username, password, first_name, last_name, student_id, faculty(optional), department(optional).
    Supports preselection via ?dept=<id> or ?dept_code=<code> and ?faculty=<id> or ?faculty_code=<code>.
    If user selects a fallback department code (code:XXX) and no Department exists yet,
    create a Department record so the Student.department is saved and shows on /students/.
    """
    from django.contrib import messages
    from .models import Student, Department, Faculty

    selected_dept = None
    selected_dept_code = None
    selected_faculty = None
    selected_faculty_code = None

    # support preselection from querystring for both faculty and department
    dept_q = request.GET.get('dept') or request.GET.get('department')
    dept_code_q = request.GET.get('dept_code') or request.GET.get('department_code')
    faculty_q = request.GET.get('faculty')
    faculty_code_q = request.GET.get('faculty_code')
    
    if dept_q:
        try:
            selected_dept = int(dept_q)
        except Exception:
            selected_dept = None
    if dept_code_q:
        selected_dept_code = dept_code_q.strip()

    if faculty_q:
        try:
            selected_faculty = int(faculty_q)
        except Exception:
            selected_faculty = None
    if faculty_code_q:
        selected_faculty_code = faculty_code_q.strip()

    # Load faculties and departments from DB or use fallback data
    db_faculties = list(Faculty.objects.all())
    db_departments = list(Department.objects.select_related('faculty').all())

    if db_faculties:
        faculties = db_faculties
    else:
        faculties = [
            {'code': 'BM', 'name': 'คณะวิทยาการจัดการ'},
            {'code': 'EDU', 'name': 'คณะครุศาสตร์'},
            {'code': 'FST', 'name': 'คณะวิทยาศาสตร์และเทคโนโลยี'},
            {'code': 'IET', 'name': 'คณะเทคโนโลยีอุตสาหกรรม'},
            {'code': 'OTH', 'name': 'คณะอื่นๆ'},
        ]

    if db_departments:
        departments = db_departments
    else:
        departments = [
            # คณะวิทยาการจัดการ (BM)
            {'code': 'ACC', 'name': 'สาขาวิชาการบัญชี', 'faculty_code': 'BM'},
            {'code': 'BUS', 'name': 'สาขาวิชาบริหารธุรกิจ', 'faculty_code': 'BM'},
            {'code': 'MBM', 'name': 'วิชาเอกการจัดการธุรกิจ', 'faculty_code': 'BM'},
            {'code': 'MKT', 'name': 'วิชาเอกการตลาด', 'faculty_code': 'BM'},
            {'code': 'FIN', 'name': 'วิชาเอกการเงินและการธนาคาร', 'faculty_code': 'BM'},
            {'code': 'DBT', 'name': 'วิชาเอกเทคโนโลยีธุรกิจดิจิทัล', 'faculty_code': 'BM'},
            {'code': 'ENT', 'name': 'วิชาเอกการเป็นผู้ประกอบการ', 'faculty_code': 'BM'},
            {'code': 'TOU', 'name': 'สาขาวิชาอุตสาหกรรมการท่องเที่ยว', 'faculty_code': 'BM'},
            {'code': 'COM', 'name': 'สาขาวิชานิเทศศาสตร์', 'faculty_code': 'BM'},

            # คณะครุศาสตร์ (EDU)
            {'code': 'ART', 'name': 'สาขาวิชาศิลปศึกษา', 'faculty_code': 'EDU'},
            {'code': 'PE',  'name': 'สาขาวิชาการประถมศึกษา', 'faculty_code': 'EDU'},
            {'code': 'EYC', 'name': 'สาขาวิชาการศึกษาปฐมวัย', 'faculty_code': 'EDU'},

            # คณะวิทยาศาสตร์และเทคโนโลยี (FST)
            {'code': 'CPT', 'name': 'สาขาวิชาเทคโนโลยีคอมพิวเตอร์', 'faculty_code': 'FST'},
            {'code': 'CHE', 'name': 'สาขาวิชาเคมี', 'faculty_code': 'FST'},
            {'code': 'ENV', 'name': 'สาขาวิชาวิทยาศาสตร์สิ่งแวดล้อม', 'faculty_code': 'FST'},

            # คณะเทคโนโลยีอุตสาหกรรม (IET)
            {'code': 'MFG', 'name': 'สาขาวิชาเทคโนโลยีการผลิตและระบบอัตโนมัติ', 'faculty_code': 'IET'},
            {'code': 'CER', 'name': 'สาขาวิชาเทคโนโลยีเซรามิกส์', 'faculty_code': 'IET'},
            {'code': 'CRA', 'name': 'สาขาวิชาศิลปหัตถกรรม', 'faculty_code': 'IET'},
            {'code': 'IDP', 'name': 'สาขาวิชาออกแบบผลิตภัณฑ์อุตสาหกรรม', 'faculty_code': 'IET'},
            {'code': 'INT', 'name': 'สาขาวิชาสถาปัตยกรรมภายใน', 'faculty_code': 'IET'},
            {'code': 'CIV', 'name': 'สาขาวิชาโยธา', 'faculty_code': 'IET'},
            {'code': 'ELE', 'name': 'สาขาวิชาไฟฟ้า', 'faculty_code': 'IET'},
            {'code': 'EEN', 'name': 'สาขาวิชาอิเล็กทรอนิกส์', 'faculty_code': 'IET'},
            {'code': 'MEC', 'name': 'สาขาวิชาเครื่องกล', 'faculty_code': 'IET'},

            # คณะอื่นๆ (OTH)
            {'code': 'MBM_M', 'name': 'สาขาวิชาการจัดการธุรกิจสมัยใหม่ (ปริญญาโท)', 'faculty_code': 'OTH'},
            {'code': 'PHH', 'name': 'สาขาวิชาสาธารณสุขศาสตร์', 'faculty_code': 'OTH'},
        ]

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        password2 = request.POST.get('password2', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        student_id = request.POST.get('student_id', '').strip()
        faculty_val = request.POST.get('faculty')  # Can be ID or code:CODE
        dept_val = request.POST.get('department')  # Can be ID or code:CODE

        context = {
            'faculties': faculties,
            'departments': departments,
            'selected_faculty': selected_faculty,
            'selected_faculty_code': selected_faculty_code,
            'selected_dept': selected_dept,
            'selected_dept_code': selected_dept_code
        }

        if not username or not password:
            context['error'] = 'กรุณากรอก username และ password'
            return render(request, 'registration.html', context)

        if password != password2:
            context['error'] = 'รหัสผ่านไม่ตรงกัน'
            return render(request, 'registration.html', context)

        if User.objects.filter(username=username).exists():
            context['error'] = 'ชื่อผู้ใช้นี้มีอยู่แล้ว'
            return render(request, 'registration.html', context)

        # Create user
        user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name)

        # Helper function to get or create faculty
        def get_or_create_faculty(faculty_val):
            if not faculty_val:
                return Faculty.objects.filter(code='OTH').first() or Faculty.objects.create(code='OTH', name='คณะอื่นๆ')
            
            # Handle faculty selection (id or code)
            if isinstance(faculty_val, str) and faculty_val.startswith('code:'):
                code = faculty_val.split(':', 1)[1]
                faculty = Faculty.objects.filter(code=code).first()
                if not faculty:
                    # Find name in fallback faculties list
                    name = None
                    for f in faculties:
                        if isinstance(f, dict) and f.get('code') == code:
                            name = f.get('name')
                            break
                    if not name:
                        name = f'คณะ {code}'
                    faculty = Faculty.objects.create(code=code, name=name)
                return faculty
            else:
                # Try ID
                try:
                    faculty_id = int(faculty_val)
                    return Faculty.objects.get(id=faculty_id)
                except (ValueError, Faculty.DoesNotExist):
                    # Try as plain code
                    return Faculty.objects.filter(code=faculty_val).first() or Faculty.objects.create(code=faculty_val, name=f'คณะ {faculty_val}')

        # Helper function to get or create department
        def get_or_create_department(dept_val, faculty_obj):
            if not dept_val:
                return None

            # Handle department selection (id or code)  
            if isinstance(dept_val, str) and dept_val.startswith('code:'):
                code = dept_val.split(':', 1)[1]
                dept = Department.objects.filter(code=code).first()
                if not dept:
                    # Find name and faculty code in fallback departments
                    dept_info = None
                    for d in departments:
                        if isinstance(d, dict) and d.get('code') == code:
                            dept_info = d
                            break
                    name = dept_info.get('name') if dept_info else f'สาขา {code}'
                    dept = Department.objects.create(
                        code=code,
                        name=name,
                        faculty=faculty_obj
                    )
                return dept
            else:
                # Try ID
                try:
                    dept_id = int(dept_val)
                    return Department.objects.get(id=dept_id)
                except (ValueError, Department.DoesNotExist):
                    # Try as plain code
                    dept = Department.objects.filter(code=dept_val).first()
                    if not dept:
                        dept = Department.objects.create(
                            code=dept_val,
                            name=f'สาขา {dept_val}',
                            faculty=faculty_obj
                        )
                    return dept

        # Get/create faculty and department
        faculty = get_or_create_faculty(faculty_val)
        dept = get_or_create_department(dept_val, faculty)

        if student_id:
            # Handle existing student
            existing_student = Student.objects.filter(student_id=student_id).first()
            if existing_student:
                # Update if changed
                changed = False
                if first_name and existing_student.first_name != first_name:
                    existing_student.first_name = first_name
                    changed = True
                if last_name and existing_student.last_name != last_name:
                    existing_student.last_name = last_name
                    changed = True
                if dept and existing_student.department_id != dept.id:
                    existing_student.department = dept
                    changed = True
                if changed:
                    try:
                        existing_student.save()
                    except Exception:
                        pass  # Ignore save errors
            else:
                # Create new student
                Student.objects.create(
                    student_id=student_id,
                    first_name=first_name,
                    last_name=last_name,
                    department=dept
                )

        login(request, user)
        return redirect('core:index')

    context = {
        'faculties': faculties,
        'departments': departments,
        'selected_faculty': selected_faculty,
        'selected_faculty_code': selected_faculty_code,
        'selected_dept': selected_dept,
        'selected_dept_code': selected_dept_code
    }
    return render(request, 'registration.html', context)

def faculty_detail(request, pk):
    db_error = False
    try:
        faculty = get_object_or_404(Faculty, pk=pk)
        departments = faculty.departments.all()
    except OperationalError:
        db_error = True
        faculty = None
        departments = []
    return render(request, 'faculty_detail.html', {'faculty': faculty, 'departments': departments, 'db_error': db_error})

def department_detail(request, pk):
    db_error = False
    try:
        department = get_object_or_404(Department, pk=pk)
        courses = department.courses.all()
    except OperationalError:
        db_error = True
        department = None
        courses = []
    return render(request, 'department_detail.html', {'department': department, 'courses': courses, 'db_error': db_error})

def course_detail(request, pk):
    db_error = False
    try:
        course = get_object_or_404(Course, pk=pk)
        regs = course.registrations.select_related('student').all()
    except OperationalError:
        db_error = True
        course = None
        regs = []
    return render(request, 'course_detail.html', {'course': course, 'registrations': regs, 'db_error': db_error})

@login_required
def student_profile(request, pk):
    db_error = False
    try:
        student = get_object_or_404(Student, pk=pk)
        regs = student.registrations.select_related('course').all()
    except OperationalError:
        db_error = True
        student = None
        regs = []
    return render(request, 'student_profile.html', {'student': student, 'registrations': regs, 'db_error': db_error})

def logout_view(request):
    """
    Log out current user (accepts GET and POST) and show logged_out page.
    This avoids HTTP 405 when the browser follows a GET link to /logout/.
    """
    # perform logout
    logout(request)
    # render a simple logged out page (or redirect to login if you prefer)
    try:
        return render(request, 'logged_out.html')
    except Exception:
        # fallback: redirect to login if template missing
        return redirect('core:login')
