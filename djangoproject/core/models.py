from django.db import models

GRADE_CHOICES = [
    ('A', 'A'),
    ('B', 'B'),
    ('C', 'C'),
    ('D', 'D'),
    ('F', 'F'),
    ('I', 'Incomplete'),
]

COURSE_STATUS = [
    ('R', 'Required'),
    ('E', 'Elective'),
    ('M', 'Major-only'),
]

REG_STATUS = [
    ('DRAFT', 'Draft'),
    ('CONFIRMED', 'Confirmed'),
]

class Faculty(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name

class Department(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, blank=True)
    faculty = models.ForeignKey(Faculty, related_name='departments', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Course(models.Model):
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    units = models.PositiveIntegerField(default=3)
    department = models.ForeignKey(Department, related_name='courses', on_delete=models.CASCADE)

    # New fields:
    status = models.CharField(max_length=1, choices=COURSE_STATUS, default='R')  # Required/Elective/Major-only
    capacity = models.PositiveIntegerField(default=40)
    instructor = models.CharField(max_length=200, blank=True)
    # Simple schedule string (e.g. "Mon 09:00-11:00,Wed 09:00-11:00") - used for naive clash detection
    schedule = models.CharField(max_length=300, blank=True)
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='required_for')

    def __str__(self):
        return f"{self.code} - {self.name}"

class Student(models.Model):
    student_id = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, related_name='students', on_delete=models.SET_NULL, null=True, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"{self.student_id} - {self.first_name} {self.last_name}"

class Registration(models.Model):
    student = models.ForeignKey(Student, related_name='registrations', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='registrations', on_delete=models.CASCADE)
    year = models.PositiveIntegerField()
    semester = models.CharField(max_length=20)
    units = models.PositiveIntegerField()
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # New field for draft vs confirmed
    status = models.CharField(max_length=10, choices=REG_STATUS, default='CONFIRMED')

    class Meta:
        unique_together = ('student', 'course', 'year', 'semester')

    def __str__(self):
        return f"{self.student} - {self.course} ({self.year}/{self.semester})"
