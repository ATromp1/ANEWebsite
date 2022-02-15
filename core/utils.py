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
                        # event_status = "benched"
                        event_status_cssclass = event_status

                        calendarhtml += "<div class='calendar-grid-event-name'>%s</div>" % event_name
                        calendarhtml += "<a href='/events/%s' class='calendar-grid-event-btn %s'>%s</a>" % (
                            events[id]['event_date'],
                            event_status_cssclass, event_status)

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
    return SocialAccount.objects.filter(user=request.user).first().extra_data


def set_user_late(request, event_date):
    event_obj = RaidEvent.objects.get(date=event_date)
    current_user_account_id = get_current_user_data(request)['sub']
    event_obj.add_late_user(current_user_account_id=current_user_account_id)
    return redirect('events')


def remove_user_late(request, event_date):
    event_obj = RaidEvent.objects.get(date=event_date)
    current_user_account_id = get_current_user_data(request)['sub']
    event_obj.rem_late_user(current_user_account_id=current_user_account_id)
    return redirect('events')


def rem_user_from_roster_button(request, event_date):
    """
    removes all characters belonging to the currently logged-in user and remove them from the initial roster
    sent in the event/details view. Also removes the user from Late list if it exists.
    """
    event_obj = RaidEvent.objects.get(date=event_date)
    current_user_account_id = get_current_user_data(request)
    event_obj.remove_char_from_roster(current_user_id=current_user_account_id['sub'])
    remove_late_user_if_declined(event_date)
    return redirect('events')


def remove_late_user_if_declined(event_date):
    late_user_obj = LateUser.objects.filter(raid_event=RaidEvent.objects.get(date=event_date))
    if late_user_obj.exists():
        late_user_obj.delete()


def add_user_to_roster_button(request, event_date):
    """Current user can sign himself back in, if signed off before."""
    event_obj = RaidEvent.objects.get(date=event_date)
    current_user_account_id = get_current_user_data(request)['sub']
    event_obj.attend_raid(current_user_account_id)
    return redirect('events')


def delete_event(request, event_date):
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


def even_view_late_to_db(request):
    """
    Reacts to ajax get request from event view. Minutes late gets stored into db after the button is pressed and
    submitted.
    """
    if request.GET.get('date') is not None:
        date = request.GET.get('date')
        minutes_late = request.GET.get('minutes_late')

        if LateUser.objects.filter(raid_event=RaidEvent.objects.get(date=date)).exists():
            print("DATE ALREADY EXISTS")
            obj = LateUser.objects.get(raid_event=RaidEvent.objects.get(date=date))
            obj.minutes_late = minutes_late
            obj.save()

        else:
            LateUser.objects.create(raid_event=RaidEvent.objects.get(date=date),
                                    minutes_late=minutes_late,
                                    user=MyUser.objects.get(user=request.user))


def event_details_ajax(event_date, request):
    """
    Overarching function that takes in the ajax request when a role button is clicked in frontend.
    If no roster exists for that particular boss on that date, a new object will be created or otherwise updated.
    After creating/updating the object, the update_selected_roster method is called to update the selected player in
    the database.
    """
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
    """
    Upon clicking a tank/healer/melee/ranged icon while creating the active roster for a boss in the front end,
    the back end will be updated with the selected player name and will therefore either be removed or added.
    """
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

    return 'benched'


def sync_bnet(request):
    """
    If new user logs in via battlenet, their characters will be fetched by API and
    their class and account_id will be linked in Roster.
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

