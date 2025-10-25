from django.core.management.base import BaseCommand
from core.models import Faculty, Department

class Command(BaseCommand):
    help = 'Seed database with faculty and major data structure'

    def handle(self, *args, **options):
        # Data structure for faculties
        faculties_data = [
            {'id': 'F001', 'code': 'SCI', 'name': 'คณะวิทยาศาสตร์และเทคโนโลยี'},
            {'id': 'F002', 'code': 'EDU', 'name': 'คณะครุศาสตร์'},
            {'id': 'F003', 'code': 'ENG', 'name': 'คณะวิศวกรรมศาสตร์'},
            {'id': 'F004', 'code': 'BUS', 'name': 'คณะบริหารธุรกิจ'},
            {'id': 'F005', 'code': 'HUM', 'name': 'คณะมนุษยศาสตร์และสังคมศาสตร์'},
            {'id': 'F006', 'code': 'MED', 'name': 'คณะแพทยศาสตร์'},
            {'id': 'F007', 'code': 'LAW', 'name': 'คณะนิติศาสตร์'},
            {'id': 'F008', 'code': 'AGR', 'name': 'คณะเกษตรศาสตร์'},
            {'id': 'F009', 'code': 'ART', 'name': 'คณะศิลปกรรมศาสตร์'},
            {'id': 'F010', 'code': 'IT', 'name': 'คณะเทคโนโลยีสารสนเทศ'},
        ]

        # Data structure for majors/departments
        majors_data = [
            # วิทย์ (F001)
            {'id': 'M001', 'code': 'CSC', 'name': 'วิทยาการคอมพิวเตอร์', 'faculty_id': 'F001'},
            {'id': 'M002', 'code': 'MAT', 'name': 'คณิตศาสตร์', 'faculty_id': 'F001'},
            {'id': 'M003', 'code': 'CHE', 'name': 'เคมี', 'faculty_id': 'F001'},
            {'id': 'M004', 'code': 'PHY', 'name': 'ฟิสิกส์', 'faculty_id': 'F001'},
            {'id': 'M005', 'code': 'BIO', 'name': 'ชีววิทยา', 'faculty_id': 'F001'},
            {'id': 'M006', 'code': 'STA', 'name': 'สถิติและข้อมูลวิทยา', 'faculty_id': 'F001'},
            {'id': 'M007', 'code': 'ENV', 'name': 'วิทยาศาสตร์สิ่งแวดล้อม', 'faculty_id': 'F001'},
            
            # ครุศาสตร์ (F002)
            {'id': 'M008', 'code': 'CED', 'name': 'คอมพิวเตอร์ศึกษา', 'faculty_id': 'F002'},
            {'id': 'M009', 'code': 'THA', 'name': 'ภาษาไทย', 'faculty_id': 'F002'},
            {'id': 'M010', 'code': 'MED', 'name': 'คณิตศาสตร์ศึกษา', 'faculty_id': 'F002'},
            {'id': 'M011', 'code': 'PRM', 'name': 'ประถมศึกษา', 'faculty_id': 'F002'},
            {'id': 'M012', 'code': 'ECE', 'name': 'ปฐมวัยศึกษา', 'faculty_id': 'F002'},
            {'id': 'M013', 'code': 'ENG', 'name': 'ภาษาอังกฤษ', 'faculty_id': 'F002'},
            {'id': 'M014', 'code': 'SCI', 'name': 'วิทยาศาสตร์ศึกษา', 'faculty_id': 'F002'},

            # วิศวะ (F003)
            {'id': 'M015', 'code': 'CE', 'name': 'วิศวกรรมโยธา', 'faculty_id': 'F003'},
            {'id': 'M016', 'code': 'EE', 'name': 'วิศวกรรมไฟฟ้า', 'faculty_id': 'F003'},
            {'id': 'M017', 'code': 'ME', 'name': 'วิศวกรรมเครื่องกล', 'faculty_id': 'F003'},
            {'id': 'M018', 'code': 'CPE', 'name': 'วิศวกรรมคอมพิวเตอร์', 'faculty_id': 'F003'},

            # บริหาร (F004)
            {'id': 'M019', 'code': 'MGT', 'name': 'การจัดการ', 'faculty_id': 'F004'},
            {'id': 'M020', 'code': 'MKT', 'name': 'การตลาด', 'faculty_id': 'F004'},
            {'id': 'M021', 'code': 'ACC', 'name': 'การบัญชี', 'faculty_id': 'F004'},
            {'id': 'M022', 'code': 'HRM', 'name': 'การจัดการทรัพยากรมนุษย์', 'faculty_id': 'F004'},

            # มนุษย์ (F005)
            {'id': 'M023', 'code': 'SOC', 'name': 'สังคมวิทยา', 'faculty_id': 'F005'},
            {'id': 'M024', 'code': 'HIS', 'name': 'ประวัติศาสตร์', 'faculty_id': 'F005'},
            {'id': 'M025', 'code': 'LAN', 'name': 'ภาษาต่างประเทศ', 'faculty_id': 'F005'},
            {'id': 'M026', 'code': 'PSY', 'name': 'จิตวิทยา', 'faculty_id': 'F005'},

            # แพทย์ (F006)
            {'id': 'M027', 'code': 'MED', 'name': 'แพทยศาสตร์ทั่วไป', 'faculty_id': 'F006'},
            {'id': 'M028', 'code': 'NUR', 'name': 'พยาบาลศาสตร์', 'faculty_id': 'F006'},

            # นิติ (F007)
            {'id': 'M029', 'code': 'LAW', 'name': 'นิติศาสตร์', 'faculty_id': 'F007'},

            # เกษตร (F008)
            {'id': 'M030', 'code': 'AGR', 'name': 'เกษตรศาสตร์', 'faculty_id': 'F008'},
            {'id': 'M031', 'code': 'AFO', 'name': 'ประมง', 'faculty_id': 'F008'},

            # ศิลปกรรม (F009)
            {'id': 'M032', 'code': 'ART', 'name': 'ศิลปะ', 'faculty_id': 'F009'},
            {'id': 'M033', 'code': 'MUS', 'name': 'ดนตรี', 'faculty_id': 'F009'},

            # ไอที (F010) 
            {'id': 'M034', 'code': 'IT', 'name': 'เทคโนโลยีสารสนเทศ', 'faculty_id': 'F010'},
            {'id': 'M035', 'code': 'CYB', 'name': 'ความมั่นคงไซเบอร์', 'faculty_id': 'F010'},
        ]

        # Create faculties
        faculty_map = {}  # To store faculty objects for department creation
        for f_data in faculties_data:
            faculty, created = Faculty.objects.get_or_create(
                code=f_data['code'],
                defaults={'name': f_data['name']}
            )
            if not created and faculty.name != f_data['name']:
                faculty.name = f_data['name']
                faculty.save()
            faculty_map[f_data['id']] = faculty
            self.stdout.write(f"{'Created' if created else 'Updated'} faculty: {faculty.name}")

        # Create departments/majors
        for m_data in majors_data:
            faculty = faculty_map.get(m_data['faculty_id'])
            if not faculty:
                self.stdout.write(self.style.WARNING(f"Faculty not found for {m_data['name']}"))
                continue
                
            dept, created = Department.objects.get_or_create(
                code=m_data['code'],
                defaults={
                    'name': m_data['name'],
                    'faculty': faculty
                }
            )
            if not created:
                # Update name if changed
                if dept.name != m_data['name'] or dept.faculty != faculty:
                    dept.name = m_data['name']
                    dept.faculty = faculty
                    dept.save()
            self.stdout.write(f"{'Created' if created else 'Updated'} department: {dept.name}")

        self.stdout.write(self.style.SUCCESS('Successfully seeded faculty and major data'))