from datetime import datetime
from datetime import timedelta

from allauth.socialaccount.models import SocialAccount
from django.shortcuts import render, redirect

from core.forms import Eventform
from core.models import Roster, RaidEvent, populate_roster_db, get_guild_roster, update_guild_roster_classes


# @login_required(login_url='/accounts/battlenet/login/?process=login&next=%2F')
def home_view(request):
    template_name = 'home.html'
    context = {
        'social_user': get_user_display_name(request),
    }
    return render(request, template_name, context)


def login_user_button(request):
    return redirect('/accounts/battlenet/login/?process=login')


def events_view(request):
    template_name = 'events.html'

    event_list = RaidEvent.objects.all()
    context = {
        'event_list': event_list,
        'social_user': get_user_display_name(request),
    }
    return render(request, template_name, context)


def add_event(request):
    submitted = False
    if request.method == "POST":
        form = Eventform(request.POST)
        if form.is_valid():
            form.save()
            api_roster = get_guild_roster(request)
            populate_roster_db(api_roster)
            update_guild_roster_classes()
            date = request.POST['date']
            RaidEvent.objects.get(date=date).populate_roster()
            return redirect('events')
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


def delete_event(request, raidevent_id):
    event = RaidEvent.objects.get(pk=raidevent_id)
    if request.user.is_staff:
        event.delete()
        return redirect('events')
    else:
        return redirect('events')


def events_details_view(request, raidevent_id):
    event_obj = RaidEvent.objects.get(pk=raidevent_id)
    roster = event_obj.roster.all()

    template_name = 'events_details.html'
    context = {
        'event': event_obj,
        'roster': roster,
        'social_user': get_user_display_name(request),
    }
    return render(request, template_name, context)


def get_current_user_id(request):
    return SocialAccount.objects.filter(user=request.user).first().extra_data


def rem_user_from_roster_button(request, raidevent_id):
    event_obj = RaidEvent.objects.get(pk=raidevent_id)
    current_user_account_id = get_current_user_id(request)['sub']
    event_obj.remove_char_from_roster(current_user_id=current_user_account_id)
    return redirect('events-details', raidevent_id=event_obj.id)


def add_user_to_roster_button(request, raidevent_id):
    event_obj = RaidEvent.objects.get(pk=raidevent_id)
    current_user_account_id = get_current_user_id(request)['sub']
    event_obj.sign_in(current_user_account_id)
    return redirect('events-details', raidevent_id=event_obj.id)


def roster_view(request):
    template_name = 'roster.html'
    context = {
        'roster': Roster.objects.all(),
        'social_user': get_user_display_name(request),
    }
    return render(request, template_name, context)


def calendar_view(request):
    template_name = 'calendar.html'

    events = RaidEvent.objects.all()
    events_dict = {}
    for event in events:
        try:
            event_name = event.name
        except AttributeError:
            event_name = "Raid"

        events_dict.update({event.id: {
            'event_name': event_name,
            'event_date': event.date,
            'event_id': event.id,
            # 'currentUser_status': currentUser_status,

        }})

    cal = generate_calendar(events_dict)

    context = {
        'cal': cal,
        'social_user': get_user_display_name(request),
    }
    return render(request, template_name, context)


def get_user_display_name(request):
    if request.user.is_authenticated:
        if request.user.is_anonymous:
            user = 'Anonymous'
        else:
            user = get_current_user_id(request)['battletag']
    else:
        user = 'Not logged in'
    return user


def generate_calendar(events):
    weeks_to_show = 3
    days_to_show = weeks_to_show * 7

    # current_date.weekday() returns a number from 0-6 so create a dict to translate it to a string

    days_of_week = {
        0: "Mon",
        1: "Tues",
        2: "Wednes",
        3: "Thurs",
        4: "Fri",
        5: "Satur",
        6: "Sun",
    }

    # Calendar should start on wednesday - Get current weekday and go back x days to get to last wednesday
    # Current date
    current_date = datetime.now()
    day_of_week = current_date.weekday()  # 0 - 6
    # How far to go back to get to last wednesday
    # weekday from current_date.weekday(): how far to go back
    deltadays = {
        0: 5,
        1: 6,
        2: 0,
        3: 1,
        4: 2,
        5: 3,
        6: 4,
    }
    # timedelta() adds/removes X amount of days from current_date
    last_wednesday = current_date - timedelta(deltadays.get(day_of_week))

    # string to send to page - formatted as html
    calendarhtml = ""
    for day in range(days_to_show):
        day_in_future = last_wednesday + timedelta(day)
        # current refers to the day in the future
        current_day_of_month = day_in_future.day
        day_of_week = day_in_future.weekday()
        current_month = day_in_future.month

        # If day is todays date make it highlighted
        day_status = ""
        if day_in_future == current_date:
            day_status = "active"

        # If day is before todays date disable it
        if day_in_future < current_date:
            day_status = "disabled"

        calendarhtml += "<div class='calendar-grid-item %s calendar-day-%s'>" % (
            day_status, days_of_week.get(day_of_week))
        calendarhtml += "<div class='calendar-grid-date'>%s-%s</div>" % (
            current_day_of_month, current_month)
        calendarhtml += "<div class='calendar-grid-item-content'>"

        for id in events:
            # Index == ID
            if events[id]['event_date'].day == current_day_of_month:
                if events[id]['event_date'].month == current_month:
                    event_name = events[id]['event_name']

                    #    event_status = events[index]['event_status']
                    event_status = "benched"
                    event_status_cssclass = event_status

                    calendarhtml += "<div class='calendar-grid-event-name'>%s</div>" % event_name
                    calendarhtml += "<a href='/events/%s' class='calendar-grid-event-btn %s'>%s</a>" % (events[id]['event_id'],
                                                                                                        event_status_cssclass, event_status)

        calendarhtml += "</div></div>"

    return calendarhtml
