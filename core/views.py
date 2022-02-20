from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from core.forms import Eventform
from core.models import (
    Roster,
    RaidEvent,
    Boss,
    LateUser,
    MyUser
)

from core.utils import (
    get_playable_classes_as_css_classes,
    generate_calendar,
    get_user_display_name, select_player_ajax, create_roster_dict, selected_roster_from_db_to_json,
    user_attendance_status, save_late_user, load_roster_template, get_user_chars_per_event,
    is_user_absent, get_user_rank
)


def home_view(request):
    events = RaidEvent.objects.all().order_by('date')
    
    is_officer = False
    if request.user.is_authenticated:
        is_officer = get_user_rank(request)
        if events.exists():
            for event in events:
                event.status = user_attendance_status(event, request)

                if is_user_absent(event, request):
                    event.absent = True
    
    save_late_user(request, request.GET)
    context = {
        'upcoming_event': events[0],
        'social_user': get_user_display_name(request),
        'is_officer': is_officer,
    }
    return render(request, 'home.html', context)


@login_required(login_url='/accounts/battlenet/login/?process=login')
def events_view(request):
    events = RaidEvent.objects.all().order_by('date')

    if events.exists():
        for event in events:
            event.status = user_attendance_status(event, request)

            if is_user_absent(event, request):
                event.absent = True

    save_late_user(request, request.GET)

    context = {
        'event_list': events,
        'social_user': get_user_display_name(request),
        'is_officer': get_user_rank(request),
    }
    return render(request, 'events.html', context)


def add_event_view(request):
    if request.user.is_superuser:
        return redirect('home')
    submitted = False
    if request.method == "POST":
        form = Eventform(request.POST)
        if form.is_valid():
            form.save()
            date = request.POST['date']
            print(date)
            RaidEvent.objects.get(date=date).populate_roster()
            return redirect('events')
    else:
        form = Eventform
        if 'submitted' in request.GET:
            submitted = True

    context = {
        'form': form,
        'submitted': submitted,
        'social_user': get_user_display_name(request),
        'is_officer': get_user_rank(request),
    }
    return render(request, 'add_event.html', context)


@login_required(login_url='/accounts/battlenet/login/?process=login')
def events_details_view(request, event_date):
    current_raid = RaidEvent.objects.get(date=event_date)

    load_roster_template(current_raid, request.GET)
    select_player_ajax(request.GET, current_raid)

    check_user_in_late_users = LateUser.objects.filter(user=MyUser.objects.get(user=request.user),
                                                       raid_event=current_raid).exists()

    context = {
        'user_char_selected': get_user_chars_per_event(current_raid, request),
        'roster_dict': create_roster_dict(current_raid),
        'bosses': serializers.serialize("json", Boss.objects.all()),
        'css_classes': get_playable_classes_as_css_classes(),
        'selected_roster': selected_roster_from_db_to_json(current_raid),
        'late_users': LateUser.objects.filter(raid_event=current_raid),
        'event_date': event_date,
        'user_is_late': check_user_in_late_users,
        'user_is_absent': is_user_absent(current_raid, request),
        'social_user': get_user_display_name(request),
        'is_officer': get_user_rank(request),
    }
    return render(request, 'events_details.html', context)


def roster_view(request):
    context = {
        'roster': Roster.objects.all(),
        'playable_classes': get_playable_classes_as_css_classes(),
        'social_user': get_user_display_name(request),
        'is_officer': get_user_rank(request),
    }
    return render(request, 'roster.html', context)


@login_required(login_url='/accounts/battlenet/login/?process=login')
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
        'is_officer': get_user_rank(request),
    }
    return render(request, 'calendar.html', context)
