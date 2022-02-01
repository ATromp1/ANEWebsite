import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from allauth.socialaccount.models import SocialAccount, SocialToken
import requests

from players.models import CurrentUser, Roster
from django.db import IntegrityError

from players.utils import json_extract

@login_required(login_url='/accounts/battlenet/login/?process=login&next=%2F')
def home_view(request):
    template_name = 'home.html'

    api_profiles = get_profile_summary(request)
    populate_char_db(api_profiles)
    api_roster = get_guild_roster()

    populate_roster_db(api_roster)


    context = {
        'social_accounts': SocialAccount.objects.all(),
        'social_user': SocialAccount.objects.filter(user=request.user).first().extra_data['battletag'],
        'roster': Roster.objects.all(),
    }

    return render(request, template_name, context)

def roster_view(request):
    template_name = 'roster.html'
    context = {
        'roster': Roster.objects.all()
    }
    return render(request, template_name, context)

def populate_roster_db(api_roster):
    ranks = [0, 1, 3, 4, 5]
    for member in api_roster['members']:
        rank = member['rank']
        character = member['character']['name']
        CurrentUser.objects.filter(name=character).update(rank=rank)
        if rank in ranks:
            Roster.objects.filter(name=character).update_or_create(name=character, rank=rank)


def get_profile_summary(request):

    print("Current user: ", SocialAccount.objects.filter(user=request.user))
    access_token = SocialToken.objects.all().first()
    header = {
        'Authorization': 'Bearer %s' % access_token,
    }
    response = requests.get('https://eu.api.blizzard.com/profile/user/wow?namespace=profile-eu&locale=en_US',
                            headers=header)
    result = response.json()
    return result


def get_guild_roster():
    access_token = SocialToken.objects.all().first()
    header = {
        'Authorization': 'Bearer %s' % access_token,
    }
    response = requests.get(
        'https://eu.api.blizzard.com/data/wow/guild/tarren-mill/a-necessary-evil/roster?namespace=profile-eu&locale=en_US',
        headers=header)
    result = response.json()
    return result


def populate_char_db(res):
    for i in range(len(res['wow_accounts'])):
        for j in range(len(res['wow_accounts'][i]['characters'])):
            account_id = res['id']
            char_name = res['wow_accounts'][i]['characters'][j]['name']
            char_id = res['wow_accounts'][i]['characters'][j]['id']
            try:
                CurrentUser.objects.create(name=char_name, account_id=account_id, character_id=char_id)
            except IntegrityError:
                pass
