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
    add_event_view,
    edit_event,
    boss_wishes_view,
)
from core.utils import decline_raid_button, attend_raid_button, delete_event_button, logout_user_button, \
    login_user_button, sync_bnet, toggle_staff_button, roster_update_button

urlpatterns = [

    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('accounts/', include('allauth.urls')),

    path('login_user/', login_user_button, name='login-user-button'),
    path('accounts/logout/', logout_user_button, name='logout-user-button'),
    path('sync/', sync_bnet, name='sync-bnet'),
    path('toggle_staff/', toggle_staff_button, name='toggle-staff'),
    path('update_roster', roster_update_button, name='update-roster'),

    path('roster/', roster_view, name='roster'),
    path('calendar/', calendar_view, name='calendar'),

    path('events/', events_view, name='events'),
    path('events/<slug:event_date>/', events_details_view, name='events-details'),
    path('edit/<slug:event_date>/', edit_event, name='edit-event'),
    path('add_event', add_event_view, name='add-event'),
    path('delete_event/<event_date>', delete_event_button, name='delete-event'),

    path('sign_off_user/<event_date>/*', decline_raid_button, name='opt-out'),
    path('sign_in_user/<event_date>/*', attend_raid_button, name='opt-in'),
    path('boss-wishes/', boss_wishes_view, name='boss-wishes')
]
