from django.db import models
from django.contrib.auth.models import User
from csmconnect import settings
import datetime

# Create your models here.
class Meeting(models.Model):
    # dates = []
    # for i in range(7):
    #     date = datetime.datetime.now(tz=datetime.timezone(-datetime.timedelta(hours=8))) + datetime.timedelta(days=i)
    #     dates.append((date.strftime('%a, %b %d').replace(' 0', ''), date.strftime('%a, %b %d').replace(' 0', '')))
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
