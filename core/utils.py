import json
from datetime import datetime, timedelta

from allauth.socialaccount.models import SocialAccount
from django.shortcuts import redirect
from django.contrib.auth.models import Group

from core.models import RaidEvent, BossPerEvent, Boss, Roster, LateUser, MyUser, get_user_profile_data, \
    set_account_id_and_class


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

                        event_status = events[id]['event_status']
                        event_status_cssclass = event_status

                        calendarhtml += "<div class='calendar-grid-event-name'>%s</div>" % event_name
                        calendarhtml += "<a href='/events/%s' class='calendar-grid-event-btn %s'>%s</a>" % (
                            events[id]['event_date'],
                            event_status_cssclass, event_status.capitalize())

        calendarhtml += "</div></div>"

    return calendarhtml


def get_user_display_name(request):
    """
    Function to display the correct battletag in the top right of all the views
    """
    if request.user.is_superuser:
        return 'God'
    if request.user.is_authenticated:
        if request.user.is_anonymous:
            user = 'Anonymous'
        else:
            user = get_current_user_data(request)['battletag']
    else:
        user = ''
    return user


def get_current_user_data(request):
    return SocialAccount.objects.get(user=request.user).extra_data


def user_chars_in_roster(request):
    return Roster.objects.filter(account_id=get_current_user_data(request)['id'])


def decline_raid_button(request, event_date):
    """
    removes all characters belonging to the currently logged-in user and remove them from the initial roster
    sent in the event/details view. Also removes the user from Late list if it exists.
    """
    event_obj = RaidEvent.objects.get(date=event_date)
    event_obj.decline_raid(user_chars_in_roster(request))
    remove_late_user(event_obj)
    return redirect('events')


def remove_late_user(event_obj):
    late_user_obj = LateUser.objects.filter(raid_event=event_obj)
    if late_user_obj.exists():
        late_user_obj.delete()


def attend_raid_button(request, event_date):
    """Current user can sign himself back in, if signed off before."""
    event_obj = RaidEvent.objects.get(date=event_date)
    event_obj.attend_raid(user_chars_in_roster(request))
    return redirect('events')


def delete_event_button(request, event_date):
    """
    Deletes an event in the /events page and redirects back to the same page
    """
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


def even_view_late_to_db(request, ajax_data):
    """
    Reacts to ajax get request from event view. Minutes late gets stored into db after the button is pressed and
    submitted.
    """
    if ajax_data.get('date') is not None:
        date = ajax_data.get('date')
        minutes_late = ajax_data.get('minutes_late')
        current_raid = RaidEvent.objects.get(date=date)
        try:
            late_user_obj = LateUser.objects.get(raid_event=current_raid)
            if ajax_data.get('delete') == 'True':
                return late_user_obj.delete()

        except LateUser.DoesNotExist:
            LateUser.objects.create(raid_event=current_raid,
                                    minutes_late=minutes_late,
                                    user=MyUser.objects.get(user=request.user))
        else:
            LateUser.objects.filter(raid_event=current_raid).update(minutes_late=minutes_late)


def select_player_ajax(ajax_data, current_raid):
    """
    Overarching function that takes in the ajax request when a role button is clicked in frontend.
    If no roster exists for that particular boss on that date, a new object will be created or otherwise updated.
    After creating/updating the object, the update_selected_roster method is called to update the selected player in
    the database.
    """
    if ajax_data.get('name') is not None:
        role = ajax_data.get('role')
        name = ajax_data.get('name')
        boss_id = str(int(ajax_data.get('boss_id')) + 1)
        boss_obj = Boss.objects.get(id=boss_id)
        try:
            BossPerEvent.objects.get(raid_event=current_raid)
        except BossPerEvent.DoesNotExist:
            BossPerEvent.objects.create(boss=boss_obj,
                                        raid_event=current_raid)
        else:
            BossPerEvent.objects.filter(raid_event=current_raid).update(boss=boss_obj, raid_event=current_raid)

        update_selected_roster(boss_obj, name, current_raid, role)


def update_selected_roster(boss, name, raid_event, role):
    """
    Upon clicking a tank/healer/melee/ranged icon while creating the active roster for a boss in the front end,
    the database will be updated with the selected player name and will either be removed or added.
    """
    selected_boss = BossPerEvent.objects.get(raid_event=raid_event, boss=boss)
    match role:
        case 'tank':
            if selected_boss.tank.all().filter(name=name).exists():
                selected_boss.remove_from_tank(name)
            else:
                selected_boss.ajax_to_tank(name)
        case 'healer':
            if selected_boss.healer.all().filter(name=name).exists():
                selected_boss.remove_from_healer(name)
            else:
                selected_boss.ajax_to_healer(name)
        case 'rdps':
            if selected_boss.rdps.all().filter(name=name).exists():
                selected_boss.remove_from_rdps(name)
            else:
                selected_boss.ajax_to_rdps(name)
        case 'mdps':
            if selected_boss.mdps.all().filter(name=name).exists():
                selected_boss.remove_from_mdps(name)
            else:
                selected_boss.ajax_to_mdps(name)


def create_initial_roster_json(event_date):
    """
    Creates a json dictionary containing the default roster (everyone) and class except players that have signed off
    """
    roster_dict = {}
    roster_at_date = RaidEvent.objects.get(date=event_date).roster
    for character in roster_at_date.all():
        if roster_at_date.get(name=character).playable_class is not None:
            roster_dict[character.id] = {
                'name': character.name,
                'playable_class': character.playable_class
            }
    return roster_dict


def selected_roster_from_db_to_json(event_date):
    """
    Queries all selected players corresponding to all bosses in a single event date and pushes them to a
    json file that serves as context in the event-details view
    """
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


def user_attendance_status(event, request):
    user_characters = Roster.objects.filter(account_id=get_current_user_data(request)['id'])
    for user_char in user_characters:
        if not RaidEvent.objects.get(date=event.date).roster.all().filter(name=user_char).exists():
            return 'absent'
        else:
            for boss in BossPerEvent.objects.filter(raid_event=RaidEvent.objects.get(date=event.date)):
                if boss.tank.filter(name=user_char).exists():
                    return 'selected'
                if boss.healer.filter(name=user_char).exists():
                    return 'selected'
                if boss.rdps.filter(name=user_char).exists():
                    return 'selected'
                if boss.mdps.filter(name=user_char).exists():
                    return 'selected'

    boss_obj = BossPerEvent.objects.filter(raid_event=RaidEvent.objects.get(date=event.date))
    print(boss_obj)
    for boss in boss_obj:
        total_roster_count = boss.tank.count() + boss.healer.count() + boss.rdps.count() + boss.mdps.count()
        if total_roster_count < 20:
            return 'Pending'

    return 'benched'


def sync_bnet(request):
    """
    If new user logs in via battlenet, their characters will be fetched by API and
    their class and account_id will be linked in Roster. Officers will be added to a django admin group and
    given staff status.
    """
    all_user_characters = get_user_profile_data(request)
    set_account_id_and_class(all_user_characters)
    set_officer_staff(request)
    return redirect('home')


def set_officer_staff(request):
    account_id = get_current_user_data(request)['id']
    officer_ranks = [0, 1]
    user_characters = Roster.objects.filter(account_id=account_id)
    for character in user_characters:
        if character.rank in officer_ranks:
            group = Group.objects.get(name='Officers')
            request.user.groups.add(group)
            request.user.is_staff = True
            request.user.save()
            break


def load_roster_template(event_date, ajax_data):
    if ajax_data.get('saved_setup') is not None:
        boss_id = str(int(ajax_data.get('boss_id')) + 1)
        roster_to_save = ajax_data.get('saved_setup')
        json_to_object = json.loads(roster_to_save)
        tanks = [x for x in json_to_object if x['role'] == 'tank']
        healers = [x for x in json_to_object if x['role'] == 'healer']
        rdps = [x for x in json_to_object if x['role'] == 'rdps']
        mdps = [x for x in json_to_object if x['role'] == 'mdps']
        try:
            obj = BossPerEvent.objects.filter(raid_event=RaidEvent.objects.get(date=event_date)).get(
                boss=Boss.objects.get(id=boss_id))
            obj.delete()
        except BossPerEvent.DoesNotExist:
            pass

        obj = BossPerEvent.objects.create(boss=Boss.objects.get(id=boss_id),
                                          raid_event=RaidEvent.objects.get(date=event_date))
        for character in tanks:
            obj.ajax_to_tank(character['name'])
        for character in healers:
            obj.ajax_to_healer(character['name'])
        for character in rdps:
            obj.ajax_to_rdps(character['name'])
        for character in mdps:
            obj.ajax_to_mdps(character['name'])


def get_user_chars_per_event(event_date, request):
    all_user_characters = get_current_user_data(request)['id']
    user_chars_in_roster = Roster.objects.filter(account_id=all_user_characters)
    obj = BossPerEvent.objects.filter(raid_event=RaidEvent.objects.get(date=event_date))
    user_chars_selected_per_raid = {}
    for boss in obj:
        id = boss.boss.id - 1
        user_chars_selected_per_raid[id] = {}
        for char in user_chars_in_roster:
            if char in boss.tank.all():
                user_chars_selected_per_raid[id]['tank'] = {'name': char.name, 'playable_class': char.playable_class}
            if char in boss.healer.all():
                user_chars_selected_per_raid[id]['healer'] = {'name': char.name, 'playable_class': char.playable_class}
            if char in boss.rdps.all():
                user_chars_selected_per_raid[id]['rdps'] = {'name': char.name, 'playable_class': char.playable_class}
            if char in boss.mdps.all():
                user_chars_selected_per_raid[id]['mdps'] = {'name': char.name, 'playable_class': char.playable_class}
    return user_chars_selected_per_raid
