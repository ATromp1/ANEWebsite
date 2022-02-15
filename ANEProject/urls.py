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
)
from core.utils import rem_user_from_roster_button, add_user_to_roster_button, delete_event, logout_user_button, \
    login_user_button, set_user_late, remove_user_late, sync_bnet

urlpatterns = [

    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('accounts/', include('allauth.urls')),

    path('login_user/', login_user_button, name='login-user-button'),
    path('accounts/logout/', logout_user_button, name='logout-user-button'),
    path('sync/', sync_bnet, name='sync-bnet'),

    path('roster/', roster_view, name='roster'),
    path('calendar/', calendar_view, name='calendar'),

    path('events/', events_view, name='events'),
    path('events/<slug:event_date>/', events_details_view, name='events-details'),
    path('add_event', add_event_view, name='add-event'),
    path('delete_event/<event_date>', delete_event, name='delete-event'),

    path('sign_off_user/<event_date>/*', rem_user_from_roster_button, name='opt-out'),
    path('sign_in_user/<event_date>/*', add_user_to_roster_button, name='opt-in'),
    path('late/<event_date>', set_user_late, name='late-user'),
    path('notlate/<event_date>', remove_user_late, name='rem-late-user')
]
