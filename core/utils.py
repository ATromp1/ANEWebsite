from datetime import datetime, timedelta

from allauth.socialaccount.models import SocialAccount
from django.shortcuts import redirect

from core.models import RaidEvent, BossPerEvent, Boss


def get_playable_classes_as_css_classes():
    playable_classes = {
        'Warrior': 'warrior',
        'Paladin': 'paladin',
        'Hunter': 'hunter',
        'Rogue': 'rogue',
        'Priest': 'priest',
        'Shaman': 'shaman',
        'Mage': 'mage',
        'Warlock': 'warlock',
        'Monk': 'monk',
        'Druid': 'druid',
        'Demon Hunter': 'demonhunter',
        'Death Knight': 'deathknight',
    }
    return playable_classes


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
        current_year = day_in_future.year
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
            if events[id]['event_date'].year == current_year:
                if events[id]['event_date'].month == current_month:
                    if events[id]['event_date'].day == current_day_of_month:
                        event_name = events[id]['event_name']

                        #    event_status = events[index]['event_status']
                        event_status = "benched"
                        event_status_cssclass = event_status

                        calendarhtml += "<div class='calendar-grid-event-name'>%s</div>" % event_name
                        calendarhtml += "<a href='/events/%s' class='calendar-grid-event-btn %s'>%s</a>" % (
                            events[id]['event_date'],
                            event_status_cssclass, event_status)

        calendarhtml += "</div></div>"

    return calendarhtml


def get_user_display_name(request):
    if request.user.is_authenticated:
        if request.user.is_anonymous:
            user = 'Anonymous'
        else:
            user = get_current_user_id(request)['battletag']
    else:
        user = ''
    return user


def get_current_user_id(request):
    return SocialAccount.objects.filter(user=request.user).first().extra_data


def rem_user_from_roster_button(request, event_date):
    event_obj = RaidEvent.objects.get(date=event_date)
    current_user_account_id = get_current_user_id(request)['sub']
    event_obj.remove_char_from_roster(current_user_id=current_user_account_id)
    return redirect('events')


def add_user_to_roster_button(request, event_date):
    event_obj = RaidEvent.objects.get(date=event_date)
    current_user_account_id = get_current_user_id(request)['sub']
    event_obj.sign_in(current_user_account_id)
    return redirect('events-details', event_date=event_obj.date)


def delete_event(request, event_date):
    event_obj = RaidEvent.objects.get(date=event_date)
    if request.user.is_staff:
        event_obj.delete()
        return redirect('events')
    else:
        return redirect('events')


def logout_user_button():
    return redirect('/accounts/logout/')


def login_user_button(request):
    return redirect('/accounts/battlenet/login/?process=login')


def execute_ajax_request(event_date, request):
    if request.GET.get('name') is not None:
        role = request.GET.get('role')
        name = request.GET.get('name')
        boss_id = str(int(request.GET.get('boss_id')) + 1)

        BossPerEvent.objects.update_or_create(boss=Boss.objects.get(id=boss_id),
                                              raid_event=RaidEvent.objects.get(date=event_date))

        raid_event = RaidEvent.objects.get(date=event_date)
        boss = Boss.objects.get(id=boss_id)
        update_selected_roster(boss, name, raid_event, role)


def update_selected_roster(boss, name, raid_event, role):
    selected_current_event_and_boss = BossPerEvent.objects.get(raid_event=raid_event, boss=boss)
    match role:
        case 'tank':
            if selected_current_event_and_boss.tank.all().filter(name=name).exists():
                selected_current_event_and_boss.remove_from_tank(name)
            else:
                selected_current_event_and_boss.ajax_to_tank(name)
        case 'healer':
            if selected_current_event_and_boss.healer.all().filter(name=name).exists():
                selected_current_event_and_boss.remove_from_healer(name)
            else:
                selected_current_event_and_boss.ajax_to_healer(name)
        case 'rdps':
            if selected_current_event_and_boss.rdps.all().filter(name=name).exists():
                selected_current_event_and_boss.remove_from_rdps(name)
            else:
                selected_current_event_and_boss.ajax_to_rdps(name)
        case 'mdps':
            if selected_current_event_and_boss.mdps.all().filter(name=name).exists():
                selected_current_event_and_boss.remove_from_mdps(name)
            else:
                selected_current_event_and_boss.ajax_to_mdps(name)


def create_init_roster_json(event_date):
    roster_dict = {}
    for character in RaidEvent.objects.get(date=event_date).roster.all():
        roster_dict[character.id] = {
            'name': character.name,
            'playable_class': character.playable_class
        }
    return roster_dict


def selected_roster_from_db_to_json(event_date):
    roster_per_boss = BossPerEvent.objects.filter(raid_event=RaidEvent.objects.get(date=event_date))
    roster_per_boss_dict = {}
    for boss in roster_per_boss:
        boss_id = str(Boss.objects.get(boss_name=boss.boss).id - 1)
        roster_per_boss_dict[boss_id] = {}
        tanks = []
        for char in boss.tank.all():
            tanks.append(char.name)
        roster_per_boss_dict[boss_id]['tank'] = tanks
        healers = []
        for char in boss.healer.all():
            healers.append(char.name)
        roster_per_boss_dict[boss_id]['healer'] = healers
        rdps = []
        for char in boss.rdps.all():
            rdps.append(char.name)
        roster_per_boss_dict[boss_id]['rdps'] = rdps
        mdps = []
        for char in boss.mdps.all():
            mdps.append(char.name)
        roster_per_boss_dict[boss_id]['mdps'] = mdps
    return roster_per_boss_dict