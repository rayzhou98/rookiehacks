from django import forms
import datetime
from django.contrib.auth.models import User

class SignUpForm(forms.Form):
    your_name = forms.CharField(label='Your name:', max_length=100, widget=forms.TextInput(attrs={'placeholder':'Username'}))
    first_name = forms.CharField(label='First name:', max_length=100, widget=forms.TextInput(attrs={'placeholder':'First Name'}))
    last_name = forms.CharField(label='Last name:', max_length=100, widget=forms.TextInput(attrs={'placeholder':'Last Name'}))
    your_email = forms.EmailField(label='Your email:', widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    password = forms.CharField(label='Enter password:', widget=forms.PasswordInput(attrs={'placeholder':'Password'}), min_length=8, max_length=32)
    confirm_password = forms.CharField(label='Confirm password:', widget=forms.PasswordInput(attrs={'placeholder':'Confirm Password'}), min_length=8, max_length=32)
    account_type = forms.ChoiceField(label='Choose account type:', choices=[('', 'Account Type'), ('M', 'Mentor'), ('S', 'Student')])
    def clean(self):
        cd = self.cleaned_data
        password = cd.get('password')
        password_confirm = cd.get('confirm_password')
        if password != password_confirm:
            self.add_error('confirm_password', 'Passwords don\'t match.')
        if User.objects.filter(username=cd.get('your_name')).exists():
            self.add_error('your_name', "Username is already taken.")
        return cd

class ResubmitActivationEmailForm(forms.Form):
    email = forms.EmailField(label='Your email:')

class LoginForm(forms.Form):
    your_name = forms.CharField(label='Your name:', max_length=100, widget=forms.TextInput(attrs={'placeholder':'Username'}))
    password = forms.CharField(label='Enter password:', widget=forms.PasswordInput(attrs={'placeholder':'Password'}),  min_length=8, max_length=32)


class AddMeetingForm(forms.Form):
    date = forms.DateField(label="Meeting date:")
    start_time = forms.TimeField(label="Meeting start time:", error_messages={'invalid': 'Start time must be of the format HH:MM AM or HH:MM PM.'})
    end_time = forms.TimeField(label="Meeting end time:", error_messages={'invalid': 'End time must be of the format HH:MM AM or HH:MM PM.'})
    location = forms.CharField(label="Location:", widget=forms.Textarea)
    description = forms.CharField(label="Description:", widget=forms.Textarea)
    def clean(self):
        cd = self.cleaned_data
        start_time = cd.get('start_time')
        end_time = cd.get('end_time')
        if start_time and end_time and end_time < start_time:
            self.add_error(None, 'Start time must be before end time.')
        if start_time and end_time and start_time < datetime.time(7, 0):
            self.add_error(None, 'Start time must be after 7:00 AM.')
        if start_time and end_time and datetime.time(19, 0) < end_time:
            self.add_error(None, 'End time must be before 7:00 PM.')
        return cd

class ChangePasswordForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    old_password = forms.CharField(label='Old password:', widget=forms.PasswordInput, min_length=8, max_length=32)
    new_password = forms.CharField(label='New password:', widget=forms.PasswordInput, min_length=8, max_length=32)
    new_password_confirm = forms.CharField(label='New password confirmation:', widget=forms.PasswordInput, min_length=8, max_length=32)
    def clean(self):
        cd = self.cleaned_data
        old_password = cd.get('old_password')
        new_password = cd.get('new_password')
        new_password_confirm = cd.get('new_password_confirm')
        if old_password and not self.user.check_password(old_password):
            self.add_error('old_password', 'Password does not match current password.')
        if new_password and new_password != new_password_confirm:
            self.add_error('new_password_confirm', 'New passwords do not match.')
