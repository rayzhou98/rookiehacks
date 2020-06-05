from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Meeting(models.Model):
    date = models.fields.DateField()
    time = models.fields.TimeField()
    location = models.fields.TextField()
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Mentor")
    student = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    description = models.fields.TextField()
    class Meta:
        permissions = [
         ("join_meeting", "Allows student to join meeting."), #Add student to student list.
         ("leave_meeting", "Allows student to leave meeting.") #Remove student from student list.
        ]
