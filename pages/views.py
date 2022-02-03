from django.contrib.auth.decorators import login_required
from django.shortcuts import render
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

    # json decode error
    # api_roster = get_guild_roster()
    #
    # populate_roster_db(api_roster)

    context = {
        'social_accounts': SocialAccount.objects.all(),
        'social_user': SocialAccount.objects.filter(user=request.user).first().extra_data['battletag'],
    }
    return render(request, template_name, context)

def events_view(request):
    template_name = 'raid_events.html'

    event_list = RaidEvent.objects.all()
    context = {
        'event_list': event_list,
    }
    return render(request, template_name, context)

def events_details_view(request, raidevent_id):
    event = RaidEvent.objects.get(pk=raidevent_id)

    roster = RaidEvent.objects.first()
    roster = roster.roster()
    template_name = 'events_details.html'
    context = {
        'event': event,
        'roster': roster,
    }
    return render(request, template_name, context)

def roster_view(request):
    template_name = 'roster.html'
    context = {
        'roster': Roster.objects.all()
    }
    return render(request, template_name, context)

def calendar_view(request):
    template_name = 'calendar.html'

    current_year = datetime.now().year
    current_month = datetime.now().month
    #create calendar
    cal = HTMLCalendar().formatmonth(current_year, current_month)
    # print("DATETIME: ", datetime.now().isocalendar().week)

    context = {
        'abc': RaidEvent.objects.all(),
        'cal': cal,
    }
    return render(request, template_name, context)


