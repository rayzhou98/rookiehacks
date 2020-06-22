from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.contenttypes.models import ContentType
from django.views.generic.edit import UpdateView, DeleteView
from .forms import SignUpForm, LoginForm, AddMeetingForm, ChangePasswordForm, ResubmitActivationEmailForm
from .models import Meeting, SiteUser
from django.http import HttpResponseRedirect
from django.contrib.auth.models import Group, User, Permission
from django.db import models
from django.contrib.auth import authenticate, login, logout
from django.template import Context, RequestContext
import json
from django.template.loader import get_template
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from extra_views import UpdateWithInlinesView, InlineFormSetFactory
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .tokens import account_activation_token
from django.contrib.sites.shortcuts import get_current_site

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
                group = Group.objects.filter(name='Mentor').exists()
                if not group:
                    group = Group(name='Mentor')
                    group.save()
                else:
                    group = Group.objects.get(name='Mentor')
            else:
                group = Group.objects.filter(name='Student').exists()
                if not group:
                    group = Group(name='Student')
                    group.save()
                else:
                    group = Group.objects.get(name='Student')
            user = User.objects.create_user(username=form.cleaned_data['your_name'], first_name=form.cleaned_data['first_name'], last_name=form.cleaned_data['last_name'], email=form.cleaned_data['your_email'],  password=form.cleaned_data['password'], is_active=False)
            user.groups.add(group)
            group.save()
            site_user = SiteUser(user=user)
            site_user.save()
            subject = 'Activate Your CSMConnect Account'
            from_email = 'katiegu@berkeley.edu'  #Todo: Change to CSMConnect Admin email!
            to = user.email
            text = get_template('activate_email.txt')
            html = get_template('activate_email.html')
            user_name = user.first_name +  " " + user.last_name
            current_site = get_current_site(request)
            context = { 'user_name': user_name, 'domain': current_site.domain, 'uid': urlsafe_base64_encode(force_bytes(user.pk)), 'token': account_activation_token.make_token(user)}
            text_content = text.render(context)
            html_content = html.render(context)
            send_mail(subject, text_content, from_email, [to], html_message=html_content, fail_silently=False)
            return HttpResponseRedirect('accountactivationsent')
        else:
            return render(request, 'signup.html', {'form': form})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SignUpForm()
        return render(request, 'signup.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.siteuser.email_confirmed = True
        user.save()
        login(request, user)
        return HttpResponseRedirect('/dashboard')
    else:
        form = ResubmitActivationEmailForm()
        return render(request, 'account_activation_invalid.html')

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
            else:
                error = "Incorrect password."
                return render(request, 'login.html', {'form': form, 'error': error})
    # if a GET (or any other method) we'll create a blank form
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def account_activation_sent(request):
    return render(request, 'account_activation_sent.html')

def mentor_check(user):
    return user.groups.filter(name="Mentor").exists()

def student_check(user):
    return user.groups.filter(name="Student").exists()

@login_required(login_url='login')
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
            if request.user.siteuser.image:
                image_url = request.user.siteuser.image.url
            else:
                image_url = '/static/scheduler/images/default-profile.png'
            return render(request, 'scheduler/meeting_add_update.html', {'form': form, 'name': request.user.username, 'non_field_errors': non_field_errors, 'title': 'Add Meeting', 'user_id': request.user.id, 'image_url': image_url})
    else:
        is_mentor = request.user.groups.filter(name="Mentor").exists()
        if is_mentor:
            form = AddMeetingForm()
            if request.user.siteuser.image:
                image_url = request.user.siteuser.image.url
            else:
                image_url = '/static/scheduler/images/default-profile.png'
            return render(request, 'scheduler/meeting_add_update.html', {'form': form, 'name': request.user.username, 'title': 'Add Meeting', 'user_id': request.user.id, 'image_url': image_url})
        else:
            open_meetings = Meeting.objects.filter(student=None)
            open_meetings = list(map(lambda meeting: {"date":  meeting.date.strftime('%a, %b %d, %Y'), 'start_time': meeting.start_time.strftime("%-I:%M %p"), 'end_time': meeting.end_time.strftime("%-I:%M %p"),  'location': meeting.location , 'description': meeting.description, 'id': meeting.id, 'mentor': {'mentor_name': meeting.mentor.username, 'mentor_email': meeting.mentor.email}}, open_meetings))
            is_mentor = 'true' if is_mentor else 'false'
            if request.user.siteuser.image:
                image_url = request.user.siteuser.image.url
            else:
                image_url = '/static/scheduler/images/default-profile.png'
            return render(request, 'frontend/calendar.html', {'meetings': json.dumps(open_meetings), 'name': request.user.username, 'is_mentor': is_mentor, 'dashboard': 'false', 'is_add': True, 'user_id': request.user.id, 'image_url': image_url})

@login_required(login_url='login')
@user_passes_test(student_check, login_url='login')
def join_meeting(request, pk):
    meeting = Meeting.objects.get(id=pk)
    if request.method == "POST":
        meeting.student = request.user
        #Sender: student, Receiver: mentor
        subject = meeting.student.username + ' Joined Your Meeting'
        from_email = meeting.student.email
        to = meeting.mentor.email
        text = get_template('join_email.txt')
        html = get_template('join_email.html')
        student_name = meeting.student.first_name +  " " + meeting.student.last_name
        mentor_name = meeting.mentor.first_name + " " + meeting.mentor.last_name
        context = { 'student_name': student_name, 'mentor_name': mentor_name, 'meeting_date': meeting.date.strftime('%a, %b %d, %Y'), 'start_time': meeting.start_time, 'end_time': meeting.end_time, 'student_email': meeting.student.email}
        text_content = text.render(context)
        html_content = html.render(context)
        send_mail(subject, text_content, from_email, [meeting.student.email], html_message=html_content, fail_silently=False)
        meeting.save()
        return HttpResponseRedirect('/dashboard')
    else:
        if request.user.siteuser.image:
            image_url = request.user.siteuser.image.url
        else:
            image_url = '/static/scheduler/images/default-profile.png'
        return render(request, 'join_meeting_confirm.html', {'meeting_date': meeting.date.strftime('%a, %b %d, %Y'), 'start_time': meeting.start_time.strftime("%-I:%M %p"), 'end_time': meeting.end_time.strftime("%-I:%M %p"), 'meeting_location': meeting.location, 'meeting_id': pk, 'name': request.user.username, 'user_id': request.user.id, 'image_url': image_url})

class EditMeeting(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Meeting
    fields = ['date', 'start_time', 'end_time', 'location', 'description']
    title = 'Edit Meeting'
    is_add = False
    template_name_suffix = '_add_update'
    login_url = 'login'
    success_url = "/dashboard"

    def get_context_data(self, **kwargs):
        context = super(EditMeeting, self).get_context_data(**kwargs)
        context['title'] = self.title
        context['name'] = self.request.user.username
        context['is_add'] = self.is_add
        context['meeting_id'] = self.kwargs['pk']
        context['user_id'] = self.request.user.id
        if self.request.user.siteuser.image:
            context['image_url'] = self.request.user.siteuser.image.url
        else:
            context['image_url'] = '/static/scheduler/images/default-profile.png'
        return context

    def test_func(self):
        return self.request.user.groups.filter(name="Mentor").exists()

    def form_valid(self, form):
        meeting = Meeting.objects.get(id=self.kwargs['pk'])
        subject = 'Meeting with ' + meeting.mentor.username + ' Updated'
        from_email = meeting.mentor.email
        if meeting.student:
            to = meeting.student.email
            text = get_template('edit_email.txt')
            html = get_template('edit_email.html')
            student_name = meeting.student.first_name +  " " + meeting.student.last_name
            mentor_name = meeting.mentor.first_name + " " + meeting.mentor.last_name
            context = { 'student_name': student_name, 'mentor_name': mentor_name, 'meeting_date': form.cleaned_data.get('date'), 'start_time': form.cleaned_data.get('start_time'), 'end_time': form.cleaned_data.get('end_time'), 'location': form.cleaned_data.get('location'), 'description': form.cleaned_data.get('description'), 'mentor_email': meeting.mentor.email}
            text_content = text.render(context)
            html_content = html.render(context)
            send_mail(subject, text_content, from_email, [meeting.student.email], html_message=html_content, fail_silently=False)
        return super(EditMeeting, self).form_valid(form)

class DeleteMeeting(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Meeting
    login_url = 'login'
    success_url = "/dashboard"

    def get_context_data(self, **kwargs):
        context = super(DeleteMeeting, self).get_context_data(**kwargs)
        context['name'] = self.request.user.username
        context['user_id'] = self.request.user.id
        if self.request.user.siteuser.image:
            context['image_url'] = self.request.user.siteuser.image.url
        else:
            context['image_url'] = '/static/scheduler/images/default-profile.png'
        return context

    def test_func(self):
        return self.request.user.groups.filter(name="Mentor").exists()

    def delete(self, request, *args, **kwargs):
        meeting = Meeting.objects.get(id=self.kwargs['pk'])
        subject = 'Meeting with ' + meeting.mentor.username + ' Cancelled'
        from_email = meeting.mentor.email
        if meeting.student:
            to = meeting.student.email
            text = get_template('delete_email.txt')
            html = get_template('delete_email.html')
            student_name = meeting.student.first_name +  " " + meeting.student.last_name
            mentor_name = meeting.mentor.first_name + " " + meeting.mentor.last_name
            context = { 'student_name': student_name, 'mentor_name': mentor_name,  'meeting_date': meeting.date.strftime('%a, %b %d, %Y'), 'start_time': meeting.start_time, 'end_time': meeting.end_time, 'mentor_email': meeting.mentor.email}
            text_content = text.render(context)
            html_content = html.render(context)
            send_mail(subject, text_content, from_email, [meeting.student.email], html_message=html_content, fail_silently=False)
        return super(DeleteMeeting, self).delete(request, *args, **kwargs)

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('logoutsuccess')

def logout_success(request):
    return render(request, 'logout_success.html')

@login_required(login_url='login')
@user_passes_test(student_check, login_url='login')
def leave_meeting(request, pk):
    meeting = Meeting.objects.get(id=pk)
    if request.method == "POST":
        subject = meeting.student.username + ' Left Your Meeting'
        from_email = meeting.student.email
        to = meeting.mentor.email
        text = get_template('leave_email.txt')
        html = get_template('leave_email.html')
        student_name = meeting.student.first_name +  " " + meeting.student.last_name
        mentor_name = meeting.mentor.first_name + " " + meeting.mentor.last_name
        context = { 'student_name': student_name, 'mentor_name': mentor_name, 'meeting_date': meeting.date.strftime('%a, %b %d, %Y'), 'start_time': meeting.start_time, 'end_time': meeting.end_time, 'student_email': meeting.student.email}
        text_content = text.render(context)
        html_content = html.render(context)
        send_mail(subject, text_content, from_email, [meeting.student.email], html_message=html_content, fail_silently=False)
        meeting.student = None
        meeting.save()
        return HttpResponseRedirect('/dashboard')
    else:
        if request.user.siteuser.image:
            image_url = request.user.siteuser.image.url
        else:
            image_url = '/static/scheduler/images/default-profile.png'
        return render(request, 'leave_meeting_confirm.html', {'meeting_date': meeting.date.strftime('%a, %b %d, %Y'), 'start_time': meeting.start_time.strftime("%-I:%M %p"), 'end_time':  meeting.end_time.strftime("%-I:%M %p"), 'meeting_location': meeting.location, 'meeting_id': pk, 'name': request.user.username, 'user_id': request.user.id, 'image_url': image_url})

@login_required(login_url='login')
def public_profile(request, pk):
    user = User.objects.get(id=pk)
    if user.siteuser.image:
        image_url = user.siteuser.image.url
    else:
        image_url = '/static/scheduler/images/default-profile.png'
    if user.siteuser.short_description:
        short_description = user.siteuser.short_description
    else:
        short_description = ''
    if user.siteuser.bio:
        bio = user.siteuser.bio
    else:
        bio = ''
    if user.siteuser.experience:
        experience = user.siteuser.experience
    else:
        experience = ''
    first_and_last = user.first_name + " " + user.last_name
    return render(request, 'public_profile.html', {'name': request.user.username, 'first_and_last': first_and_last, 'image_url': image_url, 'short_description': short_description, 'bio': bio, 'experience': experience, 'user_id': request.user.id})

@login_required(login_url='login')
def profile(request, pk):
    user = User.objects.get(id=pk)
    if user.siteuser.image:
        image_url = user.siteuser.image.url
    else:
        image_url = '/static/scheduler/images/default-profile.png'
    if user.siteuser.short_description:
        short_description = user.siteuser.short_description
    else:
        short_description = ''
    if user.siteuser.bio:
        bio = user.siteuser.bio
    else:
        bio = ''
    if user.siteuser.experience:
        experience = user.siteuser.experience
    else:
        experience = ''
    first_and_last = user.first_name + " " + user.last_name
    return render(request, 'profile.html', {'name': request.user.username, 'first_and_last': first_and_last, 'image_url': image_url, 'short_description': short_description, 'bio': bio, 'experience': experience, 'user_id': request.user.id})

class SiteUserInline(InlineFormSetFactory):
    model = SiteUser
    fields = ['short_description', 'bio', 'experience', 'image']

class EditUser(LoginRequiredMixin, UpdateWithInlinesView):
    model = User
    inlines = [ SiteUserInline ]
    fields = ['username','first_name', 'last_name', 'email']
    title = 'Edit User'
    template_name_suffix = '_update'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super(EditUser, self).get_context_data(**kwargs)
        context['title'] = self.title
        context['name'] = self.request.user.username
        context['user_id'] = self.kwargs["pk"]
        if self.request.user.siteuser.image:
            context['image_url'] = self.request.user.siteuser.image.url
        else:
            context['image_url'] = '/static/scheduler/images/default-profile.png'
        return context

    def get_success_url(self, **kwargs):
        if self.request.user.is_authenticated:
            success_url = "profile"
            return reverse(success_url, kwargs={'pk': self.kwargs['pk']})
        else:
            success_url = "login"
            return reverse(success_url)

@login_required(login_url='login')
def meeting_details(request, pk):
    meeting = Meeting.objects.get(id=pk)
    is_mentor = request.user.groups.filter(name="Mentor").exists()
    if request.user.siteuser.image:
        image_url = request.user.siteuser.image.url
    else:
        image_url = '/static/scheduler/images/default-profile.png'
    if is_mentor:
        return render(request, 'meeting_details.html', {'name': request.user.username, 'meeting_date': meeting.date.strftime('%a, %b %d, %Y'), 'start_time': meeting.start_time, 'end_time': meeting.end_time, 'meeting_location': meeting.location, 'description': meeting.description, 'student': meeting.student, 'is_mentor': is_mentor, 'id': pk, 'user_id': request.user.id, 'image_url': image_url})
    else:
        return render(request, 'meeting_details.html', {'name': request.user.username, 'meeting_date': meeting.date.strftime('%a, %b %d, %Y'), 'start_time': meeting.start_time, 'end_time': meeting.end_time, 'meeting_location': meeting.location, 'description': meeting.description, 'mentor': meeting.mentor, 'is_mentor': is_mentor, 'id': pk, 'user_id': request.user.id, 'image_url': image_url})

@login_required(login_url='login')
def change_password(request, pk):
    if request.user.siteuser.image:
        image_url = request.user.siteuser.image.url
    else:
        image_url = '/static/scheduler/images/default-profile.png'
    if request.method == 'POST':
        user = User.objects.get(id=pk)
        form = ChangePasswordForm(user, request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['new_password'])
            user.save()
            redirect_url = '/login'
            return HttpResponseRedirect(redirect_url)
        else:
            return render(request, 'password_change.html', {'name': request.user.username, 'form': form, 'user_id': request.user.id, 'image_url': image_url})
    else:
        form = ChangePasswordForm(request.user)
        return render(request, 'password_change.html', {'name': request.user.username, 'form': form, 'user_id': request.user.id, 'image_url': image_url})
