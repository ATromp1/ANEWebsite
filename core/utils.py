import json
from datetime import datetime, timedelta

from allauth.socialaccount.models import SocialAccount
from django.shortcuts import redirect
from django.contrib.auth.models import Group

from core.models import RaidEvent, BossPerEvent, Boss, Roster, LateUser, MyUser, get_user_profile_data, \
    set_account_id_and_class, get_guild_roster, populate_roster_db


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


def get_coming_raid_days(amount_of_raids):
    raid_days = [0, 2, 6]  # Monday, Wednesday, Sunday
    current_day = datetime.now()

    raid_dates_in_future = []
    index = 0
    while len(raid_dates_in_future) < amount_of_raids:
        day_in_future = current_day + timedelta(index)
        index = index + 1
        if day_in_future.weekday() in raid_days:
            raid_dates_in_future.append(day_in_future)

    return raid_dates_in_future


def generate_future_events():
    for day in get_coming_raid_days(9):
        day = day.date().strftime('%Y-%m-%d')

        try:
            RaidEvent.objects.get(date=day)
        except RaidEvent.DoesNotExist:
            obj = RaidEvent.objects.create(date=day)
            obj.populate_roster()


def generate_calendar(events):
    weeks_to_show = 3
    days_to_show = weeks_to_show * 7

    # current_date.weekday() returns a number from 0-6 so create a dict to translate it to a string

    days_of_week = {
        0: "Mon",
        1: "Tues",
        2: "Wed",
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

        for index in events:
            # Index == ID
            if events[index]['event_date'].year == current_year:
                if events[index]['event_date'].month == current_month:
                    if events[index]['event_date'].day == current_day_of_month:
                        event_name = events[index]['event_name']

                        event_status = events[index]['event_status']
                        event_status_cssclass = event_status
                        if day_in_future.date() < datetime.now().date():
                            event_status_cssclass = "past"
                            event_status = "Passed"
                        calendarhtml += "<div class='calendar-grid-event-name'>%s</div>" % event_name
                        calendarhtml += "<a href='/events/%s' class='calendar-grid-event-btn %s'>%s</a>" % (
                            events[index]['event_date'],
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


def get_user_chars_in_roster(request):
    try:
        res = Roster.objects.filter(account_id=get_current_user_data(request)['id'])
    except Roster.DoesNotExist:
        pass
    else:
        return res


def decline_raid_button(request, event_date):
    """
    removes all characters belonging to the currently logged-in user and remove them from the initial roster
    sent in the event/details view. Also removes the user from Late list if it exists.
    """
    event_obj = RaidEvent.objects.get(date=event_date)
    user_chars = get_user_chars_per_event(event_obj, request)
    for boss in user_chars.keys():
        if user_chars[boss]:
            boss_obj = BossPerEvent.objects.get(raid_event=event_obj, boss=Boss.objects.get(boss_id=boss))
            role = user_chars[boss]['role']
            name = user_chars[boss]['name']
            boss_obj.remove_from_role(role, name)

    event_obj.decline_raid(get_user_chars_in_roster(request))
    remove_late_user(event_obj)

    return redirect('events')


def remove_late_user(event_obj):
    late_user_obj = LateUser.objects.filter(raid_event=event_obj)
    if late_user_obj.exists():
        late_user_obj.delete()


def attend_raid_button(request, event_date):
    """Current user can sign himself back in, if signed off before."""
    event_obj = RaidEvent.objects.get(date=event_date)
    event_obj.attend_raid(get_user_chars_in_roster(request))
    return redirect('events')


def roster_update_button(request):
    api_roster = get_guild_roster(request)
    populate_roster_db(api_roster)
    return redirect('home')


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


def get_past_events():
    events = RaidEvent.objects.all().order_by('date')
    past_events = []
    if events.exists():
        for event in events:
            if event.date < datetime.now().date():
                past_events.append(event)
    return past_events


def get_upcoming_events():
    events = RaidEvent.objects.all().order_by('date')
    upcoming_events = []
    if events.exists():
        for event in events:
            if event.date >= datetime.now().date():
                upcoming_events.append(event)
    return upcoming_events


def logout_user_button():
    return redirect('/accounts/logout/')


def login_user_button(request):
    return redirect('/accounts/battlenet/login/?process=login')


def handle_event_ajax(request, ajax_data):
    """
    Events takes 2 types of ajax request: late and decline. 
    Call different functions depending on which one is specified in type
    """
    if ajax_data.get('type') is not None:
        if ajax_data.get('type') == 'decline':
            decline_raid_button(request, ajax_data.get('date'))

        elif ajax_data.get('type') == 'attend':
            attend_raid_button(request, ajax_data.get('date'))

        elif ajax_data.get('type') == 'late':
            save_late_user(request, ajax_data)


def save_late_user(request, ajax_data):
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
        boss_id = ajax_data.get('boss_id')
        boss = Boss.objects.get(boss_id=boss_id)

        boss_obj = BossPerEvent.objects.update_or_create(boss=boss, raid_event=current_raid)

        update_selected_roster(boss_obj, name, role)


def update_selected_roster(boss, name, role):
    """
    Upon clicking a tank/healer/melee/ranged icon while creating the active roster for a boss in the front end,
    the database will be updated with the selected player name and will either be removed or added.
    """
    boss = boss[0]
    if boss.check_exists(role, name):
        boss.remove_from_role(role, name)
    else:
        boss.add_to_role(role, name)


def create_roster_dict(current_raid):
    """
    Creates a json dictionary containing the default roster (everyone) and class except players that have signed off
    """
    roster_dict = {}
    roster = current_raid.roster
    for character in roster.all():
        if roster.get(name=character).playable_class is not None:
            roster_dict[character.id] = {
                'name': character.name,
                'playable_class': character.playable_class
            }
    return roster_dict


def selected_roster_from_db_to_json(current_raid):
    """
    Queries all selected players corresponding to all bosses in a single event date and pushes them to a
    json file that serves as context in the event-details view
    """
    boss_roster = BossPerEvent.objects.filter(raid_event=current_raid)
    roster = {}
    for boss in boss_roster:
        boss_id = boss.boss.boss_id
        roster[boss_id] = {}
        tanks = []
        for char in boss.tank.all():
            tanks.append(char.name)
        roster[boss_id]['tank'] = tanks
        healers = []
        for char in boss.healer.all():
            healers.append(char.name)
        roster[boss_id]['healer'] = healers
        rdps = []
        for char in boss.rdps.all():
            rdps.append(char.name)
        roster[boss_id]['rdps'] = rdps
        mdps = []
        for char in boss.mdps.all():
            mdps.append(char.name)
        roster[boss_id]['mdps'] = mdps
    return roster


def user_attendance_status(event, request):
    for user_char in get_user_chars_in_roster(request):
        if not event.roster.all().filter(name=user_char).exists():
            return 'absent'

        for boss in BossPerEvent.objects.filter(raid_event=event):
            roles = ['tank', 'healer', 'rdps', 'mdps']
            for role in roles:
                if boss.check_exists(role, user_char):
                    return 'selected'

    boss_obj = BossPerEvent.objects.filter(raid_event=event)
    if not boss_obj.exists():
        return 'Pending'

    for boss in boss_obj:
        total_roster_count = boss.tank.count() + boss.healer.count() + boss.rdps.count() + boss.mdps.count()
        if 0 < total_roster_count < 20:
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
    try:
        user_characters = Roster.objects.filter(account_id=account_id)
    except Roster.DoesNotExist:
        pass
    else:
        for character in user_characters:
            if character.rank in officer_ranks:
                group = Group.objects.get(name='Officers')
                request.user.groups.add(group)
                request.user.is_staff = True
                request.user.save()
                break


def toggle_staff_button(request):
    if request.user.is_staff:
        request.user.is_staff = False
        request.user.save()
        return redirect('home')
    if not request.user.is_staff:
        request.user.is_staff = True
        request.user.save()
        return redirect('home')


def get_user_rank(request):
    if request.user.is_anonymous or request.user.is_superuser:
        return False
    if request.user.is_authenticated:
        account_id = get_current_user_data(request)['id']
        officer_ranks = [0, 1]
        user_characters = Roster.objects.filter(account_id=account_id)
        for character in user_characters:
            if character.rank in officer_ranks:
                return True
    return False


def load_roster_template(current_raid, ajax_data):
    if ajax_data.get('saved_setup') is not None:
        boss_id = ajax_data.get('boss_id')
        roster = json.loads(ajax_data.get('saved_setup'))

        boss_obj = Boss.objects.get(boss_id=boss_id)
        obj = BossPerEvent.objects.filter(raid_event=current_raid, boss=boss_obj)

        if obj.exists():
            obj.delete()

        obj = BossPerEvent.objects.create(boss=boss_obj, raid_event=current_raid)

        for character in roster:
            obj.add_to_role(character['role'], character['name'])


def get_user_chars_per_event(current_raid, request):
    if is_user_absent(current_raid, request):
        return {}
    obj = BossPerEvent.objects.filter(raid_event=current_raid)
    user_chars_selected_per_raid = {}
    for boss_obj in obj:
        id = boss_obj.boss.boss_id
        user_chars_selected_per_raid[id] = {}
        for char in get_user_chars_in_roster(request):
            if char in boss_obj.tank.all():
                user_chars_selected_per_raid[id] = {'name': char.name, 'playable_class': char.playable_class,
                                                    'role': 'tank'}
            if char in boss_obj.healer.all():
                user_chars_selected_per_raid[id] = {'name': char.name, 'playable_class': char.playable_class,
                                                    'role': 'healer'}
            if char in boss_obj.rdps.all():
                user_chars_selected_per_raid[id] = {'name': char.name, 'playable_class': char.playable_class,
                                                    'role': 'rdps'}
            if char in boss_obj.mdps.all():
                user_chars_selected_per_raid[id] = {'name': char.name, 'playable_class': char.playable_class,
                                                    'role': 'mdps'}
    return user_chars_selected_per_raid


def is_user_absent(event, request):
    account_id = get_current_user_data(request)['id']
    # try:
    if event.roster.filter(account_id=Roster.objects.filter(account_id=account_id).first().account_id).exists():
        return False
    else:

    # except RaidEvent.DoesNotExist:
    #     all_user_characters = get_user_profile_data(request)
    #     set_account_id_and_class(all_user_characters)
        return True
