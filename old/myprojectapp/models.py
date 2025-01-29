# # Create your models here.

# from django.db import models

# class Face(models.Model):
#     userid = models.IntegerField(unique=True)
#     face_enc = models.TextField()
# from django.db import models

# class User(models.Model):
#     full_name = models.CharField(max_length=100)
#     employee_id = models.CharField(max_length=20, unique=True)
#     access = models.CharField(max_length=50)

# class Face(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     face_enc = models.TextField()


from django.db import models
import uuid
from django.utils import timezone


class User(models.Model):
    full_name = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=20, unique=True)
    access = models.CharField(max_length=50)

class Face(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    face_enc = models.TextField()



class UserEntryExit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)
    door = models.CharField(max_length=255)
    entryexit = models.CharField(max_length=10)





class Schedule(models.Model):
    title = models.CharField(max_length=100)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('ontime', 'On Time'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(default=timezone.now)



