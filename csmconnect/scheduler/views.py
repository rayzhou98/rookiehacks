from django.shortcuts import render
from django.views.generic import TemplateView
from .forms import SignUpForm, LoginForm
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
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
            is_staff = form.cleaned_data['account_type'] == "M"
            user = User.objects.create_user(form.cleaned_data['your_name'], form.cleaned_data['your_email'],  form.cleaned_data['password'], is_staff=is_staff)
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
        print("Form:")
        print(form)
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
    return render(request, 'dashboard.html', {'name': request.user.username, 'is_staff': request.user.is_staff})
