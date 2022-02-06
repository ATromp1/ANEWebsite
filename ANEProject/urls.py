"""ANEProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path, include

from core.views import (
    home_view,
    roster_view,
    calendar_view,
    events_view,
    events_details_view,
    rem_user_from_roster_button,
    add_user_to_roster_button,
    add_event,
    login_user_button,
    delete_event,
    boss_view,
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('accounts/', include('allauth.urls')),
    path('login_user/', login_user_button, name='login-user-button'),
    path('roster/', roster_view, name='roster'),
    path('calendar/', calendar_view, name='calendar'),
    path('events/', events_view, name='events'),
    path('events/<slug:event_date>/', events_details_view, name='events-details'),
    path('events/<slug:event_date>/<slug:boss_name>', boss_view, name='boss'),
    path('add_event', add_event, name='add-event'),
    path('delete_event/<event_date>', delete_event, name='delete-event'),
    path('sign_off_user/<event_date>/*', rem_user_from_roster_button, name='opt-out'),
    path('sign_in_user/<event_date>/*', add_user_to_roster_button, name='opt-in'),

]
