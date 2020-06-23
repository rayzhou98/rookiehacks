from django.shortcuts import render
from django.http import HttpResponseRedirect
from scheduler.models import Meeting
import json
from django.contrib.auth.decorators import login_required

# Create your views here.
# @login_required(login_url='login')
def dashboard(request):
    is_mentor = request.user.groups.filter(name="Mentor").exists()
    if is_mentor:
        meetings = Meeting.objects.filter(mentor=request.user)
    else:
        meetings = Meeting.objects.filter(student=request.user)
    if len(meetings) != 0:
        meetings = list(map(lambda meeting:  {"date":  meeting.date.strftime('%a, %b %d, %Y'), 'start_time': meeting.start_time.strftime("%-I:%M %p"), 'end_time': meeting.end_time.strftime("%-I:%M %p"),  'location': meeting.location , 'description': meeting.description, 'id': meeting.id, 'student': {'student_name': meeting.student.username, 'student_email': meeting.student.email}, 'mentor': {'mentor_name': meeting.mentor.username, 'mentor_email': meeting.mentor.email}} if meeting.student else {"date":  meeting.date.strftime('%a, %b %d, %Y'), 'start_time': meeting.start_time.strftime("%-I:%M %p"), 'end_time': meeting.end_time.strftime("%-I:%M %p"), 'location': meeting.location , 'description': meeting.description, 'id': meeting.id, 'student': None, 'mentor': {'mentor_name': meeting.mentor.username, 'mentor_email': meeting.mentor.email}}, meetings))
    else:
        meetings = []
    is_mentor = 'true' if is_mentor else 'false'
    if request.user.siteuser.image:
        image_url = request.user.siteuser.image.url
    else:
        image_url = '/static/scheduler/images/default-profile.png'
    return render(request, 'frontend/calendar.html', {'name': request.user.username, 'meetings': json.dumps(meetings), 'is_mentor': is_mentor, 'dashboard': 'true', 'user_id': request.user.id, 'image_url': image_url})
