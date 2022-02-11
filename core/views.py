from django.core import serializers

from django.shortcuts import render, redirect

from core.forms import Eventform
from core.models import (
    Roster,
    RaidEvent,
    populate_roster_db,
    get_guild_roster,
    update_guild_roster_classes,
    Boss,
    BossPerEvent
)

from core.utils import (
    get_playable_classes_as_css_classes,
    generate_calendar,
    get_user_display_name,
)


def home_view(request):
    context = {
        'social_user': get_user_display_name(request),
    }
    return render(request, 'home.html', context)


def events_view(request):
    event_list = RaidEvent.objects.all()
    context = {
        'event_list': event_list,
        'social_user': get_user_display_name(request),
    }
    return render(request, 'events.html', context)


def add_event_view(request):
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

    context = {
        'form': form,
        'submitted': submitted,
    }
    return render(request, 'add_event.html', context)


def events_details_view(request, event_date):
    event_obj = RaidEvent.objects.get(date=event_date)
    roster = event_obj.roster.all()

    # TODO: refactor this into a separate function, maybe put similar functions back into utils.py
    roster_dict = {}
    for character in roster:
        roster_dict[character.id] = {
            'name': character.name,
            'playable_class': character.playable_class
        }

    execute_ajax_request(event_date, request)

    boss_objects = Boss.objects.all()
    bosses = serializers.serialize("json", boss_objects)

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

    context = {
        'event': event_obj,
        'roster': roster,
        'roster_dict': roster_dict,
        'bosses': bosses,
        'social_user': get_user_display_name(request),
        'css_classes': get_playable_classes_as_css_classes(),
        'selected_roster': roster_per_boss_dict,
    }
    return render(request, 'events_details.html', context)


def execute_ajax_request(event_date, request):
    if request.GET.get('name') is not None:
        role = request.GET.get('role')
        name = request.GET.get('name')
        boss_id = str(int(request.GET.get('boss_id')) + 1)

        BossPerEvent.objects.update_or_create(boss=Boss.objects.get(id=boss_id),
                                              raid_event=RaidEvent.objects.get(date=event_date))

        raid_event = RaidEvent.objects.get(date=event_date)
        boss = Boss.objects.get(id=boss_id)
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


def roster_view(request):
    context = {
        'roster': Roster.objects.all(),
        'playable_classes': get_playable_classes_as_css_classes(),
        'social_user': get_user_display_name(request),
    }
    return render(request, 'roster.html', context)


def calendar_view(request):
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
    return render(request, 'calendar.html', context)
