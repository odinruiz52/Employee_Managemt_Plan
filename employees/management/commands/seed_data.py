# employees/management/commands/seed_data.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from random import choice, randint, random
from datetime import timedelta, date

from employees.models import Department, Employee
from attendance.models import Attendance, Performance

class Command(BaseCommand):
    help = "Seed database with departments, employees, attendance, and performance."

    def add_arguments(self, parser):
        # How many employees to create
        parser.add_argument('--employees', type=int, default=50, help='Number of employees (default 50)')
        # How many past days to generate attendance for
        parser.add_argument('--days', type=int, default=60, help='Days of attendance to create (default 60)')
        # Wipe existing data first?
        parser.add_argument('--wipe', action='store_true', help='Delete existing data before seeding')

    def handle(self, *args, **options):
        faker = Faker()
        num_employees = options['employees']
        days = options['days']
        wipe = options['wipe']

        if wipe:
            self.stdout.write("Wiping existing data...")
            Attendance.objects.all().delete()
            Performance.objects.all().delete()
            Employee.objects.all().delete()
            Department.objects.all().delete()

        # Create baseline departments if none
        dept_names = [
            "Engineering", "Human Resources", "Sales", "Marketing",
            "Finance", "Operations", "IT", "Customer Support"
        ]
        if Department.objects.count() == 0:
            Department.objects.bulk_create([Department(name=n) for n in dept_names])

        departments = list(Department.objects.all())

        self.stdout.write("Creating employees...")
        employees = []
        for _ in range(num_employees):
            doj = timezone.now().date() - timedelta(days=randint(30, 5 * 365))  # joined sometime in last 5 years
            emp = Employee(
                name=faker.name(),
                email=faker.unique.email(),  # unique to avoid collisions
                phone_number=faker.numerify('###-###-####'),
                address=faker.address().replace('\n', ', '),
                date_of_joining=doj,
                department=choice(departments),
            )
            employees.append(emp)
        Employee.objects.bulk_create(employees)
        employees = list(Employee.objects.all())  # refresh with IDs

        self.stdout.write("Creating attendance records...")
        attendance_bulk = []
        today = timezone.now().date()
        for emp in employees:
            # Generate attendance for past N days (skip weekends ~ simple rule)
            for d in range(days):
                day = today - timedelta(days=d)
                if day.weekday() >= 5:  # 5=Sat, 6=Sun
                    continue  # skip weekends

                # Weighted status: mostly Present
                r = random()
                if r < 0.88:
                    status = "Present"
                elif r < 0.95:
                    status = "Late"
                else:
                    status = "Absent"

                attendance_bulk.append(
                    Attendance(employee=emp, date=day, status=status)
                )
        Attendance.objects.bulk_create(attendance_bulk, batch_size=2000)

        self.stdout.write("Creating performance reviews...")
        performance_bulk = []
        for emp in employees:
            # 1–3 reviews spread after date_of_joining
            reviews = randint(1, 3)
            for _ in range(reviews):
                start = emp.date_of_joining
                if start >= today:
                    continue
                review_day = start + timedelta(days=randint(30, max(31, (today - start).days)))
                review_day = min(review_day, today)
                performance_bulk.append(
                    Performance(
                        employee=emp,
                        rating=randint(1, 5),
                        review_date=review_day
                    )
                )
        Performance.objects.bulk_create(performance_bulk)

        self.stdout.write(self.style.SUCCESS(
            f"Seeding complete: {len(employees)} employees, "
            f"{Attendance.objects.count()} attendance rows, "
            f"{Performance.objects.count()} performance rows."
        ))
