from django.shortcuts import render
from scheduler.models import Meeting
import json

# Create your views here.
def dashboard(request):
    is_mentor = request.user.groups.filter(name="Mentor").exists()
    if is_mentor:
        meetings = Meeting.objects.filter(mentor=request.user)
    else:
        meetings = Meeting.objects.filter(student=request.user)
    if len(meetings) != 0:
        meetings = list(map(lambda meeting:  {"date":  meeting.date, 'start_time': meeting.start_time.strftime("%-I:%M %p"), 'end_time': meeting.end_time.strftime("%-I:%M %p"),  'location': meeting.location , 'description': meeting.description, 'id': meeting.id, 'student': {'student_name': meeting.student.username, 'student_email': meeting.student.email}, 'mentor': {'mentor_name': meeting.mentor.username, 'mentor_email': meeting.mentor.email}} if meeting.student else {"date":  meeting.date, 'start_time': meeting.start_time.strftime("%-I:%M %p"), 'end_time': meeting.end_time.strftime("%-I:%M %p"), 'location': meeting.location , 'description': meeting.description, 'id': meeting.id, 'student': None, 'mentor': {'mentor_name': meeting.mentor.username, 'mentor_email': meeting.mentor.email}}, meetings))
    else:
        meetings = []
    return render(request, 'frontend/dashboard.html', {'name': request.user.username, 'meetings': json.dumps(meetings), 'is_mentor': is_mentor})
