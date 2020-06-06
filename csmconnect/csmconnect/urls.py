"""csmconnect URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from scheduler.views import HomeView
from scheduler import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('signup', views.sign_up, name='sign_up'),
    path('login', views.login_view, name='login'),
    path('signupsuccess', views.signupsuccess, name='signupsuccess'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('addmeeting', views.add_meeting, name='addmeeting'),
    path('editmeeting/<int:pk>', views.EditMeeting.as_view(), name="editmeeting"),
    path('deletemeeting/<int:pk>', views.DeleteMeeting.as_view(), name="deletemeeting"),
    path('logout', views.logout_view, name="logout"),
    path('logoutsuccess', views.logout_success, name="logoutsuccess"),
    path('joinmeeting/<int:pk>', views.join_meeting, name="joinmeeting"),
    path('leavemeeting/<int:pk>', views.leave_meeting, name="leavemeeting")
]
