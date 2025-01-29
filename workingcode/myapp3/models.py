from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.db import models
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone

from django.db import models
# from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from django.db import models
from django.utils import timezone
import json
from django.db import models
from django.conf import settings

from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
from datetime import timedelta, datetime
from django.utils import timezone
from django.db import models






# class CustomUserManager(BaseUserManager):
#     def create_user(self, name, password=None, **extra_fields):
#         if not name:
#             raise ValueError('The Name field must be set')
        
#         # Ensure that department and organization are required for regular users
#         if extra_fields.get('is_superuser') is not True:  # Check if it is not a superuser
#             if 'department' not in extra_fields or 'organization' not in extra_fields:
#                 raise ValueError('The Department and Organization fields must be set for regular users')

#         user = self.model(name=name, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, name, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)

#         # No need to pass is_staff and is_superuser again
#         superuser = self.model(name=name, **extra_fields)
#         superuser.set_password(password)
#         superuser.save(using=self._db)
#         return superuser


class CustomUserManager(BaseUserManager):
    def create_user(self, name, password=None, **extra_fields):
        if not name:
            raise ValueError('The Name field must be set')
        
        # Ensure that department and organization are required for regular users
        if extra_fields.get('is_superuser') is not True:  # Check if it is not a superuser
            if 'department' not in extra_fields or 'organization' not in extra_fields:
                raise ValueError('The Department and Organization fields must be set for regular users')

        user = self.model(name=name, **extra_fields)
        
        if password:  # Ensure password is set if provided
            user.set_password(password)
        else:
            raise ValueError("The Password field must be set")

        user.save(using=self._db)
        return user

    def create_superuser(self, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if password is None:
            raise ValueError("Superuser must have a password.")

        superuser = self.model(name=name, **extra_fields)
        superuser.set_password(password)
        superuser.save(using=self._db)
        return superuser





# Updated Organization Model
class Organization(models.Model):
    NAME_CHOICES = [
        ('1-10', '1-10'),
        ('11-100', '11-100'),
        ('101-1000', '101-1000'),
        ('1001-10000', '1001-10000'),
        ('10001-100000', '10001-100000'),
    ]

    name = models.CharField(max_length=255, unique=True, verbose_name="Organization Name")
    address = models.TextField(verbose_name="Organization Address")
    gst_no = models.CharField(max_length=15, verbose_name="GST No")
    no_of_employees = models.CharField(max_length=20, choices=NAME_CHOICES, verbose_name="No of Employees")
    access_control = models.BooleanField(default=False, verbose_name="Access Control")

    def __str__(self):
        return self.name




# Updated Department Model
class Department(models.Model):
    name = models.CharField(max_length=255, verbose_name="Department Name")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, verbose_name="Organization")
    integrate_with_ai_camera = models.BooleanField(default=False, verbose_name="Integrate with AI Camera")

    def __str__(self):
        return self.name







# User model
class User(AbstractBaseUser, PermissionsMixin):
    employee_code = models.CharField(max_length=10, unique=True, editable=False)  
    name = models.CharField(max_length=255, verbose_name="Name")
    role = models.CharField(max_length=20, choices=[
        ("superadmin", "Super Admin"), 
        ("hr", "HR"), 
        ("accounts", "Accounts"), 
        ("front desk", "Front desk"), 
        ("help Desk", "Help Desk"), 
        ("security", "Security"), 
        ("others", "Others")
    ], verbose_name="Role")
    photo = models.ImageField(upload_to='photos/', verbose_name="Upload Photo", null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, verbose_name="Organization", null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="Department", null=True, blank=True)
    designation = models.CharField(max_length=20, verbose_name="Designation")
    blood_group = models.CharField(max_length=3, verbose_name="Blood Group")
    emergency_contact = models.CharField(max_length=15, verbose_name="Emergency Contact Number")
    can_create_guest_pass = models.BooleanField(default=False)  # New field for guest pass permission
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_users')
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'employee_code'  
    REQUIRED_FIELDS = ['name', 'role']  

    def save(self, *args, **kwargs):
        if not self.employee_code:
            self.employee_code = self.generate_employee_code()
        super(User, self).save(*args, **kwargs)

    def generate_employee_code(self):
        last_user = User.objects.all().order_by('id').last()
        if last_user and last_user.employee_code:  # Ensure employee_code is not empty
            # Safely extract the numeric part and increment it
            try:
                employee_code_number = int(last_user.employee_code[3:])  # Extract number part
                employee_code = f"EMP{employee_code_number + 1:05d}"  # Increment and format
            except ValueError:
                # If conversion fails, start from a default value
                employee_code = "EMP00001"
        else:
            employee_code = "EMP00001"  # Start with the first employee code
        return employee_code

    def __str__(self):
        return self.name
    

# Guest model
class Guest(models.Model):
    name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='guest_photos/', null=True, blank=True)
    
    # Visiting details
    visit_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE)
    department = models.ForeignKey('Department', on_delete=models.CASCADE)
    person_to_meet = models.CharField(max_length=255, blank=True, null=True)  # Optional
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    is_approved = models.BooleanField(default=False)  # New field for approval status
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_guests')
    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name
    


# Face model
class Face(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Optional link to User
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, null=True, blank=True)  # Optional link to Guest
    face_enc = models.TextField()  # Store the face encoding as a JSON string

    def __str__(self):
        if self.user:
            return f"Face encoding for User {self.user.name}"
        elif self.guest:
            return f"Face encoding for Guest {self.guest.name}"
        return "Face encoding"

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(user__isnull=False) | ~models.Q(guest__isnull=False),
                name="only_one_user_or_guest"
            )
        ]
    




# Holiday model
class Holiday(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="HR")
    holiday_dates = models.CharField(max_length=4096)  # Comma-separated dates
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Holiday List created by {self.created_by} on {self.created_at}"




# Shift model
class Shift(models.Model):
    shift_name = models.CharField(max_length=100)
    shift_start_time = models.TimeField()
    shift_end_time = models.TimeField()
    total_work_time = models.DurationField()  # Use DurationField to store work time
    total_break_time = models.DurationField(default=timezone.timedelta())  # Auto-calculate if needed
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="HR")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.total_work_time} {self.shift_name} ({str(self.shift_start_time)} - {str(self.shift_end_time)})"



#Shift assignment model
class EmployeeShiftAssignment(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shift_assignments")
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    weekly_holiday = models.TextField()  # Use TextField to store multiple holidays as JSON
    government_holiday_applicable = models.BooleanField(default=False)
    earned_leave_qty = models.IntegerField(default=0)
    paid_leave_qty = models.IntegerField(default=0)
    casual_leave_qty = models.IntegerField(default=0)
    applicable_from = models.DateField()
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shift_assignments_made", verbose_name="Assigned by")
    created_at = models.DateTimeField(default=timezone.now)

    def set_weekly_holiday(self, holidays):
        self.weekly_holiday = json.dumps(holidays)

    def get_weekly_holiday(self):
        return json.loads(self.weekly_holiday)

    def __str__(self):
        return f"{self.employee} - {self.shift} (Assigned by {self.assigned_by})"

















# Attendance model
class Attendance(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    guest = models.ForeignKey(Guest, null=True, blank=True, on_delete=models.CASCADE)
    in_time = models.DateTimeField(null=True, blank=True)
    out_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        # ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('ontime', 'On Time'),
    ], null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.in_time and not self.guest:
            local_in_time = timezone.localtime(self.in_time)
            today_date = local_in_time.date()

            # Fetch the assigned shift for the user
            shift_assignment = EmployeeShiftAssignment.objects.filter(employee=self.user).first()

            if shift_assignment:
                shift_start_time = shift_assignment.shift.shift_start_time
                shift_end_time = shift_assignment.shift.shift_end_time

                print(f"User: {self.user}, In Time: {local_in_time.time()}, Shift Start: {shift_start_time}, Shift End: {shift_end_time}")

                # Determine status based on the entry time
                if local_in_time.time() <= shift_start_time:
                    self.status = 'ontime'
                elif shift_start_time < local_in_time.time() <= (datetime.combine(today_date, shift_start_time) + timedelta(minutes=30)).time():
                    self.status = 'late'
                else:
                    self.status = 'absent'
            print(f"Status assigned: {self.status}")

        super().save(*args, **kwargs)

    @property
    def time_spent(self):
        if self.in_time and self.out_time:
            duration = self.out_time - self.in_time
            total_seconds = int(duration.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            return f"{hours:02}:{minutes:02}"  # Format as "HH:MM"
        return "00:00"  # Default to "00:00" if no time recorded

    @property
    def date(self):
        """Extracts the date from in_time for easier access."""
        if self.in_time:
            return self.in_time.date()
        return None

    @classmethod
    def generate_daily_report(cls, date=None):
        if date is None:
            date = timezone.now().date()
        return cls.objects.filter(in_time__date=date)

    @classmethod
    def generate_weekly_report(cls, start_date=None):
        if start_date is None:
            start_date = timezone.now().date() - timedelta(days=timezone.now().weekday())  # Start of the current week
        end_date = start_date + timedelta(days=6)
        return cls.objects.filter(in_time__date__range=[start_date, end_date])

    @classmethod
    def generate_monthly_summary(cls, year, month):
        """Summarize the total time spent for each user in a given month."""
        attendances = cls.objects.filter(in_time__year=year, in_time__month=month)
        user_time_summary = {}
        guest_time_summary = {}
        

        for attendance in attendances:
            if attendance.user:
                if attendance.user not in user_time_summary:
                    user_time_summary[attendance.user] = timedelta(0)
                time_spent = convert_time_spent_to_timedelta(attendance.time_spent)
                user_time_summary[attendance.user] += time_spent
            elif attendance.guest:
                if attendance.guest not in guest_time_summary:
                    guest_time_summary[attendance.guest] = timedelta(0)
                time_spent = convert_time_spent_to_timedelta(attendance.time_spent)
                guest_time_summary[attendance.guest] += time_spent

        return {
            'user_time_summary': user_time_summary,
            'guest_time_summary': guest_time_summary,
        }
        # for attendance in attendances:
        #     if attendance.user not in user_time_summary:
        #         user_time_summary[attendance.user] = timedelta(0)
            
        #     # Assuming `time_spent` returns timedelta, we need to convert if it is string.
        #     time_spent = convert_time_spent_to_timedelta(attendance.time_spent)
        #     user_time_summary[attendance.user] += time_spent
        
        # return user_time_summary

    def __str__(self):
        # return f"{self.user.name} - {self.status}"
        if self.user:
            return f"{self.user.name} - {self.status}"
        elif self.guest:
            return f"{self.guest.name} - {self.status}"
        return "Attendance Record"

def convert_time_spent_to_timedelta(time_str):
    """Helper function to convert HH:MM string to timedelta."""
    if time_str == "00:00":
        return timedelta(0)
    hours, minutes = map(int, time_str.split(":"))
    return timedelta(hours=hours, minutes=minutes)








###Camera and lock model


from django.db import models

class Lock(models.Model):
    name = models.CharField(max_length=255, verbose_name="Lock Name")
    com_port = models.CharField(max_length=255, verbose_name="COM Port")

    def __str__(self):
        return self.name

class Camera(models.Model):
    camera_id = models.CharField(max_length=255, verbose_name="Camera ID")
    in_out = models.CharField(max_length=10, choices=[("in", "In"), ("out", "Out")], verbose_name="In/Out")
    lock = models.ForeignKey(Lock, on_delete=models.CASCADE, related_name="cameras", verbose_name="Lock ID")
    attendance = models.BooleanField(default=False, verbose_name="Attendance")

    def __str__(self):
        return self.camera_id






# New CameraSetup model for additional camera setup requirements
class CameraSetup(models.Model):
    camera = models.OneToOneField(Camera, on_delete=models.CASCADE, related_name="setup", verbose_name="Camera")
    name = models.CharField(max_length=255, verbose_name="Camera Name")
    integrate_with_access_control = models.BooleanField(default=False, verbose_name="Integrate with Access Control")
    entry_exit = models.CharField(
        max_length=10,
        choices=[("entry", "Entry"), ("exit", "Exit")],
        verbose_name="Entry/Exit",
        blank=True,
        null=True
    )
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="Department Deployment")

    def __str__(self):
        return f"Setup for {self.camera.camera_id}"

    def save(self, *args, **kwargs):
        if not self.integrate_with_access_control:
            self.entry_exit = None  # Clear entry/exit if not integrating with access control
        super().save(*args, **kwargs)





# # Custom User Manager
# class CustomUserManager(BaseUserManager):
#     def create_user(self, name, role=None, **extra_fields):
#         if not name:
#             raise ValueError('The Name field must be set')
#         if role not in ['HR', 'Accounts']:
#             raise ValueError('Superuser can only create users with HR or Accounts role')

#         # Create the user without setting a password
#         user = self.model(name=name, role=role, **extra_fields)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, name, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#         extra_fields.setdefault('role', Role.objects.get(name='Superuser'))  # Superuser role
        
#         return self.create_user(name, role='Superuser', password=password, **extra_fields)


# from django.db import models
# from django.utils import timezone
# import face_recognition
# import numpy as np

# class User(AbstractBaseUser, PermissionsMixin):
#     employee_code = models.CharField(max_length=10, unique=True, editable=False)  
#     name = models.CharField(max_length=255, verbose_name="Name")
#     role = models.CharField(max_length=20, choices=[
#         ("superadmin", "Super Admin"), 
#         ("hr", "HR"), 
#         ("accounts", "Accounts"), 
#         ("front desk", "Front desk"), 
#         ("help Desk", "Help Desk"), 
#         ("security", "Security"), 
#         ("others", "Others")
#     ], verbose_name="Role")
#     photo = models.ImageField(upload_to='photos/', verbose_name="Upload Photo", null=True, blank=True)
#     organization = models.ForeignKey(Organization, on_delete=models.CASCADE, verbose_name="Organization", null=True, blank=True)
#     department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="Department", null=True, blank=True)
#     designation = models.CharField(max_length=20, verbose_name="Designation")
#     blood_group = models.CharField(max_length=3, verbose_name="Blood Group")
#     emergency_contact = models.CharField(max_length=15, verbose_name="Emergency Contact Number")
#     can_create_guest_pass = models.BooleanField(default=False)  # New field for guest pass permission
#     is_staff = models.BooleanField(default=False)
#     is_superuser = models.BooleanField(default=False)
#     created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_users')
#     date_joined = models.DateTimeField(default=timezone.now)
#     face_encoding = models.BinaryField(null=True, blank=True)  # New field to store face encoding

#     objects = CustomUserManager()

#     USERNAME_FIELD = 'employee_code'  
#     REQUIRED_FIELDS = ['name', 'role']  

#     def save(self, *args, **kwargs):
#         # Generate an employee code if not already set
#         if not self.employee_code:
#             self.employee_code = self.generate_employee_code()

#         # Generate and store the face encoding if a photo is uploaded
#         if self.photo and not self.face_encoding:
#             try:
#                 # Load the image and extract the face encoding
#                 image = face_recognition.load_image_file(self.photo.path)
#                 face_encodings = face_recognition.face_encodings(image)
                
#                 if face_encodings:
#                     self.face_encoding = face_encodings[0].tobytes()  # Save the encoding as binary data
#             except Exception as e:
#                 print(f"Error generating face encoding: {e}")

#         super(User, self).save(*args, **kwargs)

#     def generate_employee_code(self):
#         last_user = User.objects.all().order_by('id').last()
#         if last_user and last_user.employee_code:  # Ensure employee_code is not empty
#             # Safely extract the numeric part and increment it
#             try:
#                 employee_code_number = int(last_user.employee_code[3:])  # Extract number part
#                 employee_code = f"EMP{employee_code_number + 1:05d}"  # Increment and format
#             except ValueError:
#                 # If conversion fails, start from a default value
#                 employee_code = "EMP00001"
#         else:
#             employee_code = "EMP00001"  # Start with the first employee code
#         return employee_code

#     def __str__(self):
#         return self.name










# class EmployeeShiftAssignment(models.Model):
#     employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shift_assignments")
#     shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
#     weekly_holiday = models.CharField(max_length=50, choices=[
#         ('Sunday', 'Sunday'),
#         ('Monday', 'Monday'),
#         ('Tuesday', 'Tuesday'),
#         ('Wednesday', 'Wednesday'),
#         ('Thursday', 'Thursday'),
#         ('Friday', 'Friday'),
#         ('Saturday', 'Saturday'),
#     ])
#     government_holiday_applicable = models.BooleanField(default=False)
#     earned_leave_qty = models.IntegerField(default=0)
#     paid_leave_qty = models.IntegerField(default=0)
#     casual_leave_qty = models.IntegerField(default=0)
#     applicable_from = models.DateField()
#     assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shift_assignments_made", verbose_name="Assigned by")
#     created_at = models.DateTimeField(default=timezone.now)

#     def __str__(self):
#         return f"{self.employee} - {self.shift} (Assigned by {self.assigned_by})"













# class Attendance(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     in_time = models.DateTimeField(null=True, blank=True)
#     out_time = models.DateTimeField(null=True, blank=True)
#     status = models.CharField(max_length=20, choices=[
#         ('present', 'Present'),
#         ('absent', 'Absent'),
#         ('late', 'Late'),
#         ('ontime', 'On Time'),
#     ], null=True, blank=True)

#     def save(self, *args, **kwargs):
#         if self.in_time:
#             local_in_time = timezone.localtime(self.in_time)
#             today_date = local_in_time.date()
#             # today_date = self.in_time.date()

#             # Fetch the assigned shift for the user
#             shift_assignment = EmployeeShiftAssignment.objects.filter(employee=self.user).first()

#             if shift_assignment:
#                 shift_start_time = shift_assignment.shift.shift_start_time
#                 shift_end_time = shift_assignment.shift.shift_end_time

#                 print(f"User: {self.user}, In Time: {local_in_time.time()}, Shift Start: {shift_start_time}, Shift End: {shift_end_time}")



#                 # Determine status based on the entry time
#                 if local_in_time.time() <= shift_start_time:
#                     self.status = 'ontime'
#                 elif shift_start_time < local_in_time.time() <= (datetime.combine(today_date, shift_start_time) + timedelta(minutes=30)).time():
#                     self.status = 'late'
#                 else:
#                     self.status = 'absent'
#             print(f"Status assigned: {self.status}")
        

#         super().save(*args, **kwargs)

#     @classmethod
#     def generate_daily_report(cls, date=None):
#         if date is None:
#             date = timezone.now().date()
#         return cls.objects.filter(in_time__date=date)

#     @classmethod
#     def generate_weekly_report(cls, start_date=None):
#         if start_date is None:
#             start_date = timezone.now().date() - timedelta(days=timezone.now().weekday())  # Start of the current week
#         end_date = start_date + timedelta(days=6)
#         return cls.objects.filter(in_time__date__range=[start_date, end_date])

#     def __str__(self):
#         return f"{self.user.name} - {self.status}"


















# from django.db import models
# from django.utils import timezone
# from datetime import timedelta, datetime

# class Attendance(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     in_time = models.DateTimeField(null=True, blank=True)
#     out_time = models.DateTimeField(null=True, blank=True)
#     status = models.CharField(max_length=20, choices=[
#         ('present', 'Present'),
#         ('absent', 'Absent'),
#         ('late', 'Late'),
#         ('ontime', 'On Time'),
#     ], null=True, blank=True)

#     def save(self, *args, **kwargs):
#         if self.in_time:
#             local_in_time = timezone.localtime(self.in_time)
#             today_date = local_in_time.date()

#             # Fetch the assigned shift for the user
#             shift_assignment = EmployeeShiftAssignment.objects.filter(employee=self.user).first()

#             if shift_assignment:
#                 shift_start_time = shift_assignment.shift.shift_start_time
#                 shift_end_time = shift_assignment.shift.shift_end_time

#                 print(f"User: {self.user}, In Time: {local_in_time.time()}, Shift Start: {shift_start_time}, Shift End: {shift_end_time}")

#                 # Determine status based on the entry time
#                 if local_in_time.time() <= shift_start_time:
#                     self.status = 'ontime'
#                 elif shift_start_time < local_in_time.time() <= (datetime.combine(today_date, shift_start_time) + timedelta(minutes=30)).time():
#                     self.status = 'late'
#                 else:
#                     self.status = 'absent'
#             print(f"Status assigned: {self.status}")

#         super().save(*args, **kwargs)

#     @property
#     def time_spent(self):
#         if self.in_time and self.out_time:
#             duration = self.out_time - self.in_time
#             total_seconds = int(duration.total_seconds())
#             hours, remainder = divmod(total_seconds, 3600)
#             minutes, _ = divmod(remainder, 60)
#             return f"{hours:02}:{minutes:02}"  # Format as "HH:MM"
#         return "00:00"  # Default to "00:00" if no time recorded


#     @classmethod
#     def generate_daily_report(cls, date=None):
#         if date is None:
#             date = timezone.now().date()
#         return cls.objects.filter(in_time__date=date)

#     @classmethod
#     def generate_weekly_report(cls, start_date=None):
#         if start_date is None:
#             start_date = timezone.now().date() - timedelta(days=timezone.now().weekday())  # Start of the current week
#         end_date = start_date + timedelta(days=6)
#         return cls.objects.filter(in_time__date__range=[start_date, end_date])

#     @classmethod
#     def generate_monthly_summary(cls, year, month):
#         """Summarize the total time spent for each user in a given month."""
#         attendances = cls.objects.filter(in_time__year=year, in_time__month=month)
#         user_time_summary = {}
        
#         for attendance in attendances:
#             if attendance.user not in user_time_summary:
#                 user_time_summary[attendance.user] = timedelta(0)
#             user_time_summary[attendance.user] += attendance.time_spent
        
#         return user_time_summary

#     def __str__(self):
#         return f"{self.user.name} - {self.status}"



























# class User(AbstractBaseUser, PermissionsMixin):
#     employee_code = models.CharField(max_length=10, unique=True, editable=False)  
#     name = models.CharField(max_length=255, verbose_name="Name")
#     role = models.CharField(max_length=20, choices=[("superadmin", "Super Admin"), ("hr", "HR"), ("accounts", "Accounts"), ("front desk", "Front desk"), ("help Desk", "Help Desk"), ("security", "Security"), ("others", "Others")], verbose_name="Role")
#     photo = models.ImageField(upload_to='photos/', verbose_name="Upload Photo", null=True, blank=True)
#     organization = models.ForeignKey(Organization, on_delete=models.CASCADE, verbose_name="Organization", null=True, blank=True)
    
#     # Update the department field
#     department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="Department", null=True, blank=True)
    
#     designation = models.CharField(max_length=20, verbose_name="Designation")
#     blood_group = models.CharField(max_length=3, verbose_name="Blood Group")
#     emergency_contact = models.CharField(max_length=15, verbose_name="Emergency Contact Number")
#     is_staff = models.BooleanField(default=False)
#     is_superuser = models.BooleanField(default=False)
#     created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_users')
#     date_joined = models.DateTimeField(default=timezone.now)

#     objects = CustomUserManager()

#     USERNAME_FIELD = 'employee_code'  
#     REQUIRED_FIELDS = ['name', 'role']  

#     def save(self, *args, **kwargs):
#         if not self.employee_code:
#             self.employee_code = self.generate_employee_code()
#         super(User, self).save(*args, **kwargs)

#     def generate_employee_code(self):
#         last_user = User.objects.all().order_by('id').last()
#         if last_user:
#             employee_code = f"EMP{int(last_user.employee_code[3:]) + 1:05d}"
#         else:
#             employee_code = "EMP00001"
#         return employee_code

#     def __str__(self):
#         return self.name

# # Employee/User Model
# class User(AbstractBaseUser, PermissionsMixin):
#     employee_code = models.CharField(max_length=10, unique=True, editable=False)  # Auto-generated employee code
#     name = models.CharField(max_length=255, verbose_name="Name")
#     role = models.CharField(max_length=20,null=False,blank=False, choices=[("superadmin", "Super Admin"), ("hr", "HR"), ("accounts", "Accounts"), ("front desk", "Front desk"), ("help Desk", "Help Desk"), ("security", "Security"), ("others", "Others")], verbose_name="Role")
#     photo = models.ImageField(upload_to='photos/', verbose_name="Upload Photo", null=True, blank=True)
#     organization = models.ForeignKey(Organization, on_delete=models.CASCADE, verbose_name="Organization")
#     department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="Department")
#     designation = models.CharField(max_length=20, verbose_name="Designation")
#     blood_group = models.CharField(max_length=3, verbose_name="Blood Group")
#     emergency_contact = models.CharField(max_length=15, verbose_name="Emergency Contact Number")
#     is_staff = models.BooleanField(default=False)
#     is_superuser = models.BooleanField(default=False)
#     created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_users')
#     date_joined = models.DateTimeField(default=timezone.now)

#     objects = CustomUserManager()

#     USERNAME_FIELD = 'employee_code'  # Employee code as username
#     REQUIRED_FIELDS = ['name', 'role']  # Role is required during user creation

#     def save(self, *args, **kwargs):
#         if not self.employee_code:
#             # Auto-generate employee_code if not set
#             self.employee_code = self.generate_employee_code()
#         super(User, self).save(*args, **kwargs)

#     def generate_employee_code(self):
#         last_user = User.objects.all().order_by('id').last()
#         if last_user:
#             employee_code = f"EMP{int(last_user.employee_code[3:]) + 1:05d}"
#         else:
#             employee_code = "EMP00001"
#         return employee_code

#     def __str__(self):
#         return self.name
# class User(AbstractBaseUser, PermissionsMixin):
#     employee_code = models.CharField(max_length=10, unique=True, editable=False)  
#     name = models.CharField(max_length=255, verbose_name="Name")
#     role = models.CharField(max_length=20, choices=[("superadmin", "Super Admin"), ("hr", "HR"), ("accounts", "Accounts"), ("front desk", "Front desk"), ("help Desk", "Help Desk"), ("security", "Security"), ("others", "Others")], verbose_name="Role")
#     photo = models.ImageField(upload_to='photos/', verbose_name="Upload Photo", null=True, blank=True)
#     organization = models.ForeignKey(Organization, on_delete=models.CASCADE, verbose_name="Organization")
#     department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="Department")
#     designation = models.CharField(max_length=20, verbose_name="Designation")
#     blood_group = models.CharField(max_length=3, verbose_name="Blood Group")
#     emergency_contact = models.CharField(max_length=15, verbose_name="Emergency Contact Number")
#     is_staff = models.BooleanField(default=False)
#     is_superuser = models.BooleanField(default=False)
#     created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_users')
#     date_joined = models.DateTimeField(default=timezone.now)

#     objects = CustomUserManager()

#     USERNAME_FIELD = 'employee_code'  
#     REQUIRED_FIELDS = ['name', 'role']  

#     def save(self, *args, **kwargs):
#         if not self.employee_code:
#             self.employee_code = self.generate_employee_code()
#         super(User, self).save(*args, **kwargs)

#     def generate_employee_code(self):
#         last_user = User.objects.all().order_by('id').last()
#         if last_user:
#             employee_code = f"EMP{int(last_user.employee_code[3:]) + 1:05d}"
#         else:
#             employee_code = "EMP00001"
#         return employee_code

#     def __str__(self):
#         return self.name
