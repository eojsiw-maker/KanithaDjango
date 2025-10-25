from django.core.management.base import BaseCommand
from core.models import Faculty, Department
from django.db import transaction

class Command(BaseCommand):
    help = 'Reset and seed faculty and department data'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # Clear existing data
                self.stdout.write('Deleting existing faculty and department data...')
                Department.objects.all().delete()
                Faculty.objects.all().delete()

                # Create faculties
                self.stdout.write('Creating faculties...')
                faculties = {
                    'BM': Faculty.objects.create(code='BM', name='คณะวิทยาการจัดการ'),
                    'EDU': Faculty.objects.create(code='EDU', name='คณะครุศาสตร์'),
                    'FST': Faculty.objects.create(code='FST', name='คณะวิทยาศาสตร์และเทคโนโลยี'),
                    'IET': Faculty.objects.create(code='IET', name='คณะเทคโนโลยีอุตสาหกรรม'),
                    'OTH': Faculty.objects.create(code='OTH', name='คณะอื่นๆ'),
                }

                # Create departments
                self.stdout.write('Creating departments...')
                departments_data = [
                    # คณะวิทยาการจัดการ (BM)
                    {'code': 'ACC', 'name': 'สาขาวิชาการบัญชี', 'faculty': 'BM'},
                    {'code': 'BUS', 'name': 'สาขาวิชาบริหารธุรกิจ', 'faculty': 'BM'},
                    {'code': 'MBM', 'name': 'วิชาเอกการจัดการธุรกิจ', 'faculty': 'BM'},
                    {'code': 'MKT', 'name': 'วิชาเอกการตลาด', 'faculty': 'BM'},
                    {'code': 'FIN', 'name': 'วิชาเอกการเงินและการธนาคาร', 'faculty': 'BM'},
                    {'code': 'DBT', 'name': 'วิชาเอกเทคโนโลยีธุรกิจดิจิทัล', 'faculty': 'BM'},
                    {'code': 'ENT', 'name': 'วิชาเอกการเป็นผู้ประกอบการ', 'faculty': 'BM'},
                    {'code': 'TOU', 'name': 'สาขาวิชาอุตสาหกรรมการท่องเที่ยว', 'faculty': 'BM'},
                    {'code': 'COM', 'name': 'สาขาวิชานิเทศศาสตร์', 'faculty': 'BM'},

                    # คณะครุศาสตร์ (EDU)
                    {'code': 'ART', 'name': 'สาขาวิชาศิลปศึกษา', 'faculty': 'EDU'},
                    {'code': 'PE',  'name': 'สาขาวิชาการประถมศึกษา', 'faculty': 'EDU'},
                    {'code': 'EYC', 'name': 'สาขาวิชาการศึกษาปฐมวัย', 'faculty': 'EDU'},

                    # คณะวิทยาศาสตร์และเทคโนโลยี (FST)
                    {'code': 'CPT', 'name': 'สาขาวิชาเทคโนโลยีคอมพิวเตอร์', 'faculty': 'FST'},
                    {'code': 'CHE', 'name': 'สาขาวิชาเคมี', 'faculty': 'FST'},
                    {'code': 'ENV', 'name': 'สาขาวิชาวิทยาศาสตร์สิ่งแวดล้อม', 'faculty': 'FST'},

                    # คณะเทคโนโลยีอุตสาหกรรม (IET)
                    {'code': 'MFG', 'name': 'สาขาวิชาเทคโนโลยีการผลิตและระบบอัตโนมัติ', 'faculty': 'IET'},
                    {'code': 'CER', 'name': 'สาขาวิชาเทคโนโลยีเซรามิกส์', 'faculty': 'IET'},
                    {'code': 'CRA', 'name': 'สาขาวิชาศิลปหัตถกรรม', 'faculty': 'IET'},
                    {'code': 'IDP', 'name': 'สาขาวิชาออกแบบผลิตภัณฑ์อุตสาหกรรม', 'faculty': 'IET'},
                    {'code': 'INT', 'name': 'สาขาวิชาสถาปัตยกรรมภายใน', 'faculty': 'IET'},
                    {'code': 'CIV', 'name': 'สาขาวิชาโยธา', 'faculty': 'IET'},
                    {'code': 'ELE', 'name': 'สาขาวิชาไฟฟ้า', 'faculty': 'IET'},
                    {'code': 'EEN', 'name': 'สาขาวิชาอิเล็กทรอนิกส์', 'faculty': 'IET'},
                    {'code': 'MEC', 'name': 'สาขาวิชาเครื่องกล', 'faculty': 'IET'},

                    # คณะอื่นๆ (OTH)
                    {'code': 'MBM_M', 'name': 'สาขาวิชาการจัดการธุรกิจสมัยใหม่ (ปริญญาโท)', 'faculty': 'OTH'},
                    {'code': 'PHH', 'name': 'สาขาวิชาสาธารณสุขศาสตร์', 'faculty': 'OTH'},
                ]

                for dept_data in departments_data:
                    Department.objects.create(
                        code=dept_data['code'],
                        name=dept_data['name'],
                        faculty=faculties[dept_data['faculty']]
                    )

                faculty_count = Faculty.objects.count()
                dept_count = Department.objects.count()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully created {faculty_count} faculties and {dept_count} departments'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error occurred: {str(e)}')
            )
            raise