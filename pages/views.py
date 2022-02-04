from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from allauth.socialaccount.models import SocialAccount
import calendar
from calendar import HTMLCalendar
from datetime import datetime

from pages.utils import populate_roster_db, get_profile_summary, get_guild_roster, populate_char_db
from players.models import Roster, RaidEvent, CurrentUser


@login_required(login_url='/accounts/battlenet/login/?process=login&next=%2F')
def home_view(request):
    template_name = 'home.html'

    api_profiles = get_profile_summary(request)
    populate_char_db(api_profiles)

    context = {
        'social_accounts': SocialAccount.objects.all(),
        'social_user': SocialAccount.objects.filter(user=request.user).first().extra_data['battletag'],
    }
    return render(request, template_name, context)


def events_view(request):
    template_name = 'events.html'

    event_list = RaidEvent.objects.all()
    context = {
        'event_list': event_list,
    }
    return render(request, template_name, context)


def events_details_view(request, raidevent_id):
    event = RaidEvent.objects.get(pk=raidevent_id)

    roster_in = event.event_roster()
    roster_out = event.event_sign_offs()

    template_name = 'events_details.html'
    context = {
        'event': event,
        'roster_in': roster_in,
        'roster_out': roster_out,
    }
    return render(request, template_name, context)

def update_events_details_view(request, raidevent_id):
    id = RaidEvent.objects.get(pk=raidevent_id)
    date = RaidEvent.objects.filter(pk=raidevent_id).first().date

    test = RaidEvent.objects.get(date=date)
    roster = test.event_roster()
    sign_offs = test.event_sign_offs()

    context = {
        'event': id,
        'roster': roster,
        'sign_off': sign_offs,
    }

    return render(request, 'update_event.html', context)


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
    # create calendar
    cal = HTMLCalendar().formatmonth(current_year, current_month)
    # print("DATETIME: ", datetime.now().isocalendar().week)

    context = {
        'abc': RaidEvent.objects.all(),
        'cal': cal,
    }
    return render(request, template_name, context)
