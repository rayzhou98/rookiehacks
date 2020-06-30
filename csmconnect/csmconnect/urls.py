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
from django.contrib.auth import views as auth_views
from django.urls import path, include, re_path
from scheduler.views import HomeView
from scheduler import views
from django.conf.urls.static import static
from django.conf import settings
from scheduler.forms import CustomPasswordResetForm

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('', include('frontend.urls')),
    path('signup', views.sign_up, name='signup'),
    path('login', views.login_view, name='login'),
    path('addmeeting', views.add_meeting, name='addmeeting'),
    path('meetingdetails/<int:pk>', views.meeting_details, name="meetingdetails"),
    path('editmeeting/<int:pk>', views.EditMeeting.as_view(), name="editmeeting"),
    path('deletemeeting/<int:pk>', views.DeleteMeeting.as_view(), name="deletemeeting"),
    path('logout', views.logout_view, name="logout"),
    path('logoutsuccess', views.logout_success, name="logoutsuccess"),
    path('joinmeeting/<int:pk>', views.join_meeting, name="joinmeeting"),
    path('leavemeeting/<int:pk>', views.leave_meeting, name="leavemeeting"),
    path('profile/<int:pk>', views.profile, name="profile"),
    path('editprofile/<int:pk>', views.EditUser.as_view(), name="editprofile"),
    path('publicprofile/<int:pk>', views.public_profile, name="publicprofile"),
    path('changepassword/<int:pk>', views.change_password, name='changepassword'),
    path('resetpassword', auth_views.PasswordResetView.as_view(template_name='reset_password.html'), name='resetpassword', kwargs={'form': CustomPasswordResetForm}),
    path('resetpassword/done', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('resetpassword/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name='reset_password_confirm.html'), name='password_reset_confirm'),
    path('resetpassword/complete', auth_views.PasswordResetCompleteView.as_view(template_name='reset_password_complete.html'), name='password_reset_complete'),
    path('accountactivationsent', views.account_activation_sent, name='account_activation_sent'),
    re_path(r'activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activate, name='activate')
]
