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
    event_obj = RaidEvent.objects.get(pk=raidevent_id)

    roster = event_obj.roster.all()

    template_name = 'events_details.html'
    context = {
        'event': event_obj,
        'roster': roster,
    }
    return render(request, template_name, context)


def sign_off_user(request, raidevent_id):
    event_obj = RaidEvent.objects.get(pk=raidevent_id)
    current_user_account_id = SocialAccount.objects.filter(user=request.user).first().extra_data['sub']
    event_obj.sign_off(current_user_id=current_user_account_id)
    return redirect('events-details', raidevent_id=event_obj.id)


def sign_in_user(request, raidevent_id):
    event_obj = RaidEvent.objects.get(pk=raidevent_id)
    event_obj.sign_in()
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
    # create calendar
    cal = HTMLCalendar().formatmonth(current_year, current_month)
    # print("DATETIME: ", datetime.now().isocalendar().week)

    context = {
        'abc': RaidEvent.objects.all(),
        'cal': cal,
    }
    return render(request, template_name, context)
