from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.contenttypes.models import ContentType
from django.views.generic.edit import UpdateView, DeleteView
from .forms import SignUpForm, LoginForm, AddMeetingForm
from .models import Meeting
from django.http import HttpResponseRedirect
from django.contrib.auth.models import Group, User, Permission
from django.db import models
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
import json

# Create your views here.
class HomeView(TemplateView):
    template_name = "basic-88/index.html"

def sign_up(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SignUpForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            is_mentor = form.cleaned_data['account_type'] == "M"
            content_type = ContentType.objects.get_for_model(Meeting)
            if is_mentor:
                add_permission = Permission.objects.get(codename='add_meeting', content_type=content_type)
                edit_permission = Permission.objects.get(codename='change_meeting', content_type=content_type)
                delete_permission = Permission.objects.get(codename='delete_meeting', content_type=content_type)
                view_permission = Permission.objects.get(codename='view_meeting', content_type=content_type)
                group = Group(name='Mentor')
            else:
                view_permission = Permission.objects.get(codename='view_meeting', content_type=content_type)
                join_permission = Permission.objects.get(codename='join_meeting', content_type=content_type)
                leave_permission = Permission.objects.get(codename='leave_meeting', content_type=content_type)
                group = Group(name='Student')
            user = User.objects.create_user(username=form.cleaned_data['your_name'], email=form.cleaned_data['your_email'],  password=form.cleaned_data['password'])
            group.save()
            user.groups.add(group)
            if is_mentor:
                group.permissions.set([add_permission, edit_permission, delete_permission, view_permission])
            else:
                group.permissions.set([view_permission, join_permission, leave_permission])
            return HttpResponseRedirect('signupsuccess')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form})

def login_view(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST['your_name']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            # check whether it's valid:
            if user is not None:
                login(request, user)
                # redirect to a new URL:
                return HttpResponseRedirect('dashboard')
    # if a GET (or any other method) we'll create a blank form
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def signupsuccess(request):
    return render(request, 'signupsuccess.html')

def add_meeting(request):
    if request.method == 'POST':
        form = AddMeetingForm(request.POST)
        if form.is_valid():
            #Create new meeting model, and save to database.
            meeting = Meeting(date=form.cleaned_data['date'], start_time=form.cleaned_data['start_time'], end_time=form.cleaned_data['end_time'], location=form.cleaned_data['location'], mentor=request.user, description=form.cleaned_data['description'])
            meeting.save()
            return HttpResponseRedirect('dashboard')
        else:
            non_field_errors = form.non_field_errors()
            print(non_field_errors)
            return render(request, 'scheduler/meeting_add_update.html', {'form': form, 'name': request.user.username, 'non_field_errors': non_field_errors, 'title': 'Add Meeting'})
    else:
        is_mentor = request.user.groups.filter(name="Mentor").exists()
        if is_mentor:
            form = AddMeetingForm()
            return render(request, 'scheduler/meeting_add_update.html', {'form': form, 'name': request.user.username, 'title': 'Add Meeting'})
        else:
            open_meetings = Meeting.objects.filter(student=None)
            open_meetings = list(map(lambda meeting: {"date":  meeting.date, 'start_time': meeting.start_time.strftime("%-I:%M %p"), 'end_time': meeting.end_time.strftime("%-I:%M %p"),  'location': meeting.location , 'description': meeting.description, 'id': meeting.id, 'mentor': {'mentor_name': meeting.mentor.username, 'mentor_email': meeting.mentor.email}}, open_meetings))
            is_mentor = 'true' if is_mentor else 'false'
            return render(request, 'frontend/calendar.html', {'meetings': json.dumps(open_meetings), 'name': request.user.username, 'is_mentor': is_mentor, 'dashboard': 'false'})

def join_meeting(request, pk):
    meeting = Meeting.objects.get(id=pk)
    if request.method == "POST":
        meeting.student = request.user
        meeting.save()
        return HttpResponseRedirect('/dashboard')
    else:
        return render(request, 'join_meeting_confirm.html', {'meeting_date': meeting.date, 'start_time': meeting.start_time.strftime("%-I:%M %p"), 'end_time': meeting.end_time.strftime("%-I:%M %p"), 'meeting_location': meeting.location, 'meeting_id': pk, 'name': request.user.username})

class EditMeeting(UpdateView):
    model = Meeting
    fields = ['date', 'start_time', 'end_time', 'location', 'description']
    title = 'Edit Meeting'
    template_name_suffix = '_add_update'
    success_url = "/dashboard"
    def get_context_data(self, **kwargs):
        context = super(EditMeeting, self).get_context_data(**kwargs)
        context['title'] = self.title
        context['name'] = self.request.user.username
        return context

class DeleteMeeting(DeleteView):
    model = Meeting
    success_url = "/dashboard"
    def get_context_data(self, **kwargs):
        context = super(DeleteMeeting, self).get_context_data(**kwargs)
        context['name'] = self.request.user.username
        return context

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('logoutsuccess')

def logout_success(request):
    return render(request, 'logout_success.html')

def leave_meeting(request, pk):
    meeting = Meeting.objects.get(id=pk)
    if request.method == "POST":
        meeting.student = None
        meeting.save()
        return HttpResponseRedirect('/dashboard')
    else:
        return render(request, 'leave_meeting_confirm.html', {'meeting_date': meeting.date.strftime("%m/%d/%Y"), 'meeting_time': meeting.time.strftime("%H:%M"), 'meeting_location': meeting.location, 'meeting_id': pk})

def meeting_details(request, pk):
    meeting = Meeting.objects.get(id=pk)
    is_mentor = request.user.groups.filter(name="Mentor").exists()
    if is_mentor:
        return render(request, 'meeting_details.html', {'name': request.user.username, 'meeting_date': meeting.date, 'start_time': meeting.start_time, 'end_time': meeting.end_time, 'meeting_location': meeting.location, 'description': meeting.description, 'student': meeting.student, 'is_mentor': is_mentor, 'id': pk})
    else:
        return render(request, 'meeting_details.html', {'name': request.user.username, 'meeting_date': meeting.date, 'start_time': meeting.start_time, 'end_time': meeting.end_time, 'meeting_location': meeting.location, 'description': meeting.description, 'mentor': meeting.mentor, 'is_mentor': is_mentor, 'id': pk})
