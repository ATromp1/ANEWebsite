from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from allauth.socialaccount.models import SocialAccount
import calendar
from calendar import Calendar, HTMLCalendar, TextCalendar
from datetime import datetime, date, timedelta

from calendar import HTMLCalendar
from datetime import datetime
from django.http import HttpResponseRedirect
from pages.utils import populate_roster_db, get_profile_summary, get_guild_roster, populate_char_db
from players.models import Roster, RaidEvent
from players.forms import Eventform


@login_required(login_url='/accounts/battlenet/login/?process=login&next=%2F')
def home_view(request):
    template_name = 'home.html'

    api_profiles = get_profile_summary(request)
    populate_char_db(api_profiles)

    context = {
        'social_accounts': SocialAccount.objects.all(),
        'social_user': get_current_user_id(request)['battletag'],
    }
    return render(request, template_name, context)


def events_view(request):
    template_name = 'events.html'

    event_list = RaidEvent.objects.all()
    context = {
        'event_list': event_list,
    }
    return render(request, template_name, context)


def add_event(request):
    submitted = False
    if request.method == "POST":
        form = Eventform(request.POST)
        if form.is_valid():
            form.save()
            month = request.POST['date_month']
            day = request.POST['date_day']
            year = request.POST['date_year']
            date = year + "-" + month + "-"+ day
            RaidEvent.objects.get(date=date).populate_roster()
            return HttpResponseRedirect('/add_event?submitted=True')
    else:
        form = Eventform
        if 'submitted' in request.GET:
            submitted = True

    template_name = 'add_event.html'
    context = {
        'form': form,
        'submitted': submitted,
    }
    return render(request, template_name, context)


def events_details_view(request, raidevent_id):
    event_obj = RaidEvent.objects.get(pk=raidevent_id)
    print(event_obj.date)
    roster = event_obj.roster.all()

    template_name = 'events_details.html'
    context = {
        'event': event_obj,
        'roster': roster,
    }
    return render(request, template_name, context)


def sign_off_user(request, raidevent_id):
    event_obj = RaidEvent.objects.get(pk=raidevent_id)
    current_user_account_id = get_current_user_id(request)['sub']
    event_obj.sign_off(current_user_id=current_user_account_id)
    return redirect('events-details', raidevent_id=event_obj.id)


def get_current_user_id(request):
    return SocialAccount.objects.filter(user=request.user).first().extra_data


def sign_in_user(request, raidevent_id):
    event_obj = RaidEvent.objects.get(pk=raidevent_id)
    current_user_account_id = get_current_user_id(request)['sub']
    event_obj.sign_in(current_user_account_id)
    return redirect('events-details', raidevent_id=event_obj.id)


def roster_view(request):
    template_name = 'roster.html'
    context = {
        'roster': Roster.objects.all()
    }
    return render(request, template_name, context)


def update_roster(request):
    api_roster = get_guild_roster(request)
    populate_roster_db(api_roster)

    return redirect('roster')


def calendar_view(request):
    template_name = 'calendar.html'

    current_year = datetime.now().year
    current_month = datetime.now().month

    #current_week = datetime.date(2010, 6, 16).strftime("%V")

    #create calendar
    weeks_to_show = 3
    days_to_show = weeks_to_show * 7

    days_of_week = {
        0: "Mon",
        1: "Tues",
        2: "Wednes",
        3: "Thurs",
        4: "Fri",
        5: "Satur",
        6: "Sun",
    }




    # Current date
    current_date = datetime.now() + timedelta(5)
    day_of_week = current_date.weekday() # 0 - 6
    # Start calendar on wednesday
    # How far to go back to get to last wednesday
    deltadays = {
        0: 5,
        1: 6,
        2: 0,
        3: 1,
        4: 2,
        5: 3,
        6: 4,
    }
    last_wednesday = current_date - timedelta(deltadays.get(day_of_week))

    calendarhtml = ""
    for day in range(days_to_show):
        day_in_future = last_wednesday + timedelta(day)
        current_day_of_month = day_in_future.day
        day_of_week = day_in_future.weekday()
        current_month = day_in_future.month

        day_status = ""
        if day_in_future == current_date:
            day_status = "active"

        if day_in_future < current_date:
            day_status = "disabled"

        calendarhtml += "<div class='calendar-grid-item %s calendar-day-%s'>" % (day_status, days_of_week.get(day_of_week))
        calendarhtml += "<div class='calendar-grid-item-content'>"
        calendarhtml += "<div class='calendar-grid-item-title'></div>"
        calendarhtml += "%s-%s" % (current_day_of_month, current_month)

        calendarhtml += "</div></div>"

    context = {
        'abc': RaidEvent.objects.all(),
        'cal': calendarhtml,
    }
    return render(request, template_name, context)
