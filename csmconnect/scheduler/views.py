from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView
from .forms import SignUpForm, LoginForm, AddMeetingForm
from .models import Meeting
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User, Permission
from django.db import models
from django.contrib.auth import authenticate, login

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
                edit_permission = Permission.objects.get(codename='edit_meeting', content_type=content_type)
                delete_permission = Permission.objects.get(codename='delete_meeting', content_type=content_type)
                view_permission = Permission.objects.get(codename='view_meeting', content_type=content_type)
                group = models.Group('Mentor', permissions=[add_permission, edit_permission, delete_permission, view_permission])
            else:
                view_permission = Permission.objects.get(codename='view_meeting', content_type=content_type)
                join_permission = Permission.objects.get(codename='join_meeting', content_type=content_type)
                leave_permission = Permission.objects.get(codename='leave_meeting', content_type=content_type)
                group = models.Group('Student', permissions=[view_permission, join_permission, leave_permission])
            user = User.objects.create_user(form.cleaned_data['your_name'], form.cleaned_data['your_email'],  form.cleaned_data['password'], groups=group)
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

def dashboard(request):
    #Get all meetings corresponding to the user.
    meetings = Meeting.objects.filter(mentor=request.user)
    if len(meetings) == 0:
        meetings_elements = "No meetings to show."
    else:
        meetings_elements = list(map(lambda meeting:  [meeting.date.strftime("%m/%d/%Y"),  meeting.time.strftime("%H:%M"),  meeting.location , meeting.description, meeting.id], meetings))
    return render(request, 'dashboard.html', {'name': request.user.username, 'meetings': meetings_elements})

def add_meeting(request):
    if request.method == 'POST':
        form = AddMeetingForm(request.POST)
        if form.is_valid():
            #Create new meeting model, and save to database.
            meeting = Meeting(date=form.cleaned_data['date'], time=form.cleaned_data['time'], location=form.cleaned_data['location'], mentor=request.user, description=form.cleaned_data['description'])
            meeting.save()
            return HttpResponseRedirect('dashboard')
    else:
        form = AddMeetingForm()
    return render(request, 'addmeeting.html', {'form': form, })

class EditMeeting(UpdateView):
    model = Meeting
    fields = ['date', 'time', 'location', 'description']
    template_name_suffix = '_update_form'
    success_url = "/dashboard"
