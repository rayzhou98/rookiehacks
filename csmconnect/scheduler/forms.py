from django import forms
import datetime

class SignUpForm(forms.Form):
    your_name = forms.CharField(label='Your name:', max_length=100)
    your_email = forms.EmailField(label='Your email:')
    password = forms.CharField(label='Enter password:', widget=forms.PasswordInput, min_length=8, max_length=32)
    confirm_password = forms.CharField(label='Confirm password:', widget=forms.PasswordInput, min_length=8, max_length=32)
    account_type = forms.ChoiceField(label='Choose account type:', choices=[('M', 'Mentor'), ('S', 'Student')])
    def clean(self):
        cd = self.cleaned_data
        password = cd.get('password')
        password_confirm = cd.get('confirm_password')
        if password != password_confirm:
            self.add_error('confirm_password', 'Passwords don\'t match.')
        return cd

class LoginForm(forms.Form):
    your_name = forms.CharField(label='Your name:', max_length=100)
    password = forms.CharField(label='Enter password:', widget=forms.PasswordInput, min_length=8, max_length=32)

class AddMeetingForm(forms.Form):
    # dates = []
    # for i in range(7):
    #     date = datetime.datetime.now(tz=datetime.timezone(-datetime.timedelta(hours=8))) + datetime.timedelta(days=i)
    #     dates.append((date.strftime('%a, %b %d').replace(' 0', ''), date.strftime('%a, %b %d').replace(' 0', '')))
    # date = forms.ChoiceField(label="Meeting date:", choices=dates)
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
