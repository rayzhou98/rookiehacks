from django.db import models
from django.contrib.auth.models import User
from csmconnect import settings
import datetime

# Create your models here.
class SiteUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.FileField(upload_to='uploads/')
    short_description = models.fields.TextField(blank=True, null=True)
    bio = models.fields.TextField(blank=True, null=True)
    experience = models.fields.TextField(blank=True, null=True)
    email_confirmed = models.fields.BooleanField(default=False)

class Meeting(models.Model):
    date = models.fields.DateField()
    start_time = models.fields.TimeField()
    end_time = models.fields.TimeField()
    location = models.fields.TextField()
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Mentor")
    student = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    description = models.fields.TextField()
    class Meta:
        permissions = [
         ("join_meeting", "Allows student to join meeting."), #Add student to student list.
         ("leave_meeting", "Allows student to leave meeting.") #Remove student from student list.
        ]
