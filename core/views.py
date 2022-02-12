from django.core import serializers

from django.shortcuts import render, redirect

from core.forms import Eventform
from core.models import (
    Roster,
    RaidEvent,
    populate_roster_db,
    get_guild_roster,
    Boss
)

from core.utils import (
    get_playable_classes_as_css_classes,
    generate_calendar,
    get_user_display_name, execute_ajax_request, create_initial_roster_json, selected_roster_from_db_to_json,
    user_attendance_status,
)


def home_view(request):
    context = {
        'social_user': get_user_display_name(request),
    }
    return render(request, 'home.html', context)


def events_view(request):
    global status
    events = RaidEvent.objects.all()

    for event in events:
        status = user_attendance_status(event, request)

    context = {
        'event_list': events,
        'social_user': get_user_display_name(request),
        'status': status,
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
    roster_dict = create_initial_roster_json(event_date)

    execute_ajax_request(event_date, request)

    bosses = serializers.serialize("json", Boss.objects.all())

    roster_per_boss_dict = selected_roster_from_db_to_json(event_date)

    context = {
        'roster_dict': roster_dict,
        'bosses': bosses,
        'social_user': get_user_display_name(request),
        'css_classes': get_playable_classes_as_css_classes(),
        'selected_roster': roster_per_boss_dict,
    }
    return render(request, 'events_details.html', context)


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

        status = user_attendance_status(event, request)

        events_dict.update({event.id: {
            'event_name': event_name,
            'event_date': event.date,
            'event_id': event.id,
            'event_status': status,

        }})

    cal = generate_calendar(events_dict)

    context = {
        'cal': cal,
        'social_user': get_user_display_name(request),
    }
    return render(request, 'calendar.html', context)
