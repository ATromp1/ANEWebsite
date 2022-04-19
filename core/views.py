from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from core.forms import Eventform, EditEventForm
from core.models import (
    Roster,
    RaidEvent,
    Boss,
    LateUser,
    MyUser
)

from core.utils import (
    update_boss_visibility,
    get_all_bosswishes,
    get_boss_wishes_by_account_id,
    get_current_user_data,
    get_playable_classes_as_css_classes,
    generate_calendar,
    get_user_display_name, select_player_ajax, create_roster_dict, selected_roster_from_db_to_json,
    user_attendance_status, save_late_user, load_roster_template, get_user_chars_per_event,
    is_user_absent, is_user_officer, handle_event_ajax, get_past_events, get_upcoming_events, sync_bnet,
    get_declined_users_for_event,
    publish_boss_ajax, publish_event_ajax, get_previous_raid, get_next_raid, get_all_declined_users,
    get_chars_by_account_id, boss_object_to_list, add_cssclass_to_roster_list, update_boss_wish_data
)


def sync_view(request):
    sync_bnet(request)
    return redirect('home')


def home_view(request):
    events = get_upcoming_events()
    get_all_declined_users()
    if request.user.is_authenticated:
        if events:
            for event in events:
                event.status = user_attendance_status(event, request)

    try:
        event = events[0]
    except IndexError:
        event = []

    handle_event_ajax(request, request.GET)
    context = {
        'upcoming_event': event,
        'social_user': get_user_display_name(request),
        'is_officer': is_user_officer(request),
    }
    return render(request, 'home.html', context)


@login_required(login_url='/accounts/battlenet/login/?process=login')
def events_view(request):
    events = get_upcoming_events()
    if events:
        for event in events:
            event.status = user_attendance_status(event, request)
            if is_user_absent(event, request):
                event.absent_variable = True

    save_late_user(request, request.GET)

    context = {
        'event_list': events,
        'past_events': get_past_events(),
        'social_user': get_user_display_name(request),
        'is_officer': is_user_officer(request),
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
            return redirect('events')
    else:
        form = Eventform
        if 'submitted' in request.GET:
            submitted = True

    context = {
        'form': form,
        'submitted': submitted,
        'social_user': get_user_display_name(request),
        'is_officer': is_user_officer(request),
    }
    return render(request, 'add_event.html', context)


@login_required(login_url='/accounts/battlenet/login/?process=login')
def edit_event(request, event_date):
    if request.user.is_superuser:
        return redirect('home')

    current_raid = RaidEvent.objects.get(date=event_date)
    if request.method == "POST":
        form = EditEventForm(request.POST, instance=current_raid)
        if form.is_valid():
            form.save()
            name = request.POST['name']
            RaidEvent.objects.filter(date=event_date).update(name=name)
            return redirect('events')
    else:
        form = EditEventForm(initial={
            'name': current_raid.name,
            'date': event_date,
        })

    context = {
        'form': form,
        'event': current_raid,
    }
    return render(request, 'edit_event.html', context)


@login_required(login_url='/accounts/battlenet/login/?process=login')
def events_details_view(request, event_date):
    current_raid = RaidEvent.objects.get(date=event_date)
    if current_raid in get_past_events():
        is_past_event = True
    else:
        is_past_event = False

    load_roster_template(current_raid, request.GET)
    select_player_ajax(request.GET, current_raid)
    handle_event_ajax(request, request.GET)
    publish_boss_ajax(request.GET, current_raid)
    publish_event_ajax(request.GET, current_raid)
    check_user_in_late_users = LateUser.objects.filter(user=MyUser.objects.get(user=request.user),
                                                       raid_event=current_raid).exists()

    user_minutes_late = None
    if check_user_in_late_users:
        user_minutes_late = LateUser.objects.filter(user=MyUser.objects.get(user=request.user),
                                                    raid_event=current_raid).first().minutes_late

    context = {
        'event': current_raid,
        'user_char_selected': get_user_chars_per_event(current_raid, request),
        'roster_dict': create_roster_dict(current_raid),
        'bosses': serializers.serialize("json", Boss.objects.all()),
        'css_classes': get_playable_classes_as_css_classes(),
        'selected_roster': selected_roster_from_db_to_json(current_raid),
        'late_users': LateUser.objects.filter(raid_event=current_raid),
        'declined_users': get_declined_users_for_event(request, current_raid),
        'event_date': event_date,
        'user_is_late': check_user_in_late_users,
        'user_minutes_late': user_minutes_late,
        'user_is_absent': is_user_absent(current_raid, request),
        'social_user': get_user_display_name(request),
        'is_officer': is_user_officer(request),
        'is_past_event': is_past_event,
        'next_raid': get_next_raid(current_raid),
        'previous_raid': get_previous_raid(current_raid),
    }
    return render(request, 'events_details.html', context)


@login_required(login_url='/accounts/battlenet/login/?process=login')
def boss_wishes_view(request):

    account_id = get_current_user_data(request)['id']
    user_chars = get_chars_by_account_id(account_id)

    wishes = get_boss_wishes_by_account_id(account_id)
    serialized_wishes = []
    for char in wishes:
        serialized_wishes.append(serializers.serialize("json", char))

    update_boss_wish_data(request.GET)
    update_boss_visibility(request.GET)
    context = {
        'is_officer': is_user_officer(request),
        'social_user': get_user_display_name(request),
        'bosses': boss_object_to_list(),
        'bosses_js': serializers.serialize("json", Boss.objects.all()),
        'user_chars': add_cssclass_to_roster_list(Roster.objects.filter(account_id=account_id)),
        'user_chars_js': serializers.serialize("json", user_chars),
        'boss_wishes': serialized_wishes,
        'css_classes': get_playable_classes_as_css_classes(),
        'all_char_bosswishes': get_all_bosswishes(),
    }
    return render(request, 'boss_wishes.html', context)


def roster_view(request):
    context = {
        'roster': Roster.objects.all(),
        'playable_classes': get_playable_classes_as_css_classes(),
        'social_user': get_user_display_name(request),
        'is_officer': is_user_officer(request),
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
        'is_officer': is_user_officer(request),
    }
    return render(request, 'calendar.html', context)
