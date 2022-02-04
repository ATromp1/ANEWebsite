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

from pages.views import (
    home_view,
    roster_view,
    calendar_view,
    events_view,
    events_details_view,
    update_roster,
    update_events_details_view
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('accounts/', include('allauth.urls')),
    path('roster/', roster_view, name='roster'),
    path('roster/update', update_roster, name='update-roster'),
    path('calendar/', calendar_view, name='calendar'),
    path('events/', events_view, name='events'),
    path('events/<raidevent_id>', events_details_view, name='events-details'),
    path('update_events/<raidevent_id>', update_events_details_view, name='update-events-details'),
    # path('events/<raidevent_id>/update', update_events_details_view, name='update-events-details'),

]
