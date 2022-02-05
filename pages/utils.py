import requests
from allauth.socialaccount.models import SocialAccount, SocialToken
from players.models import CurrentUser, Roster


def populate_roster_db(api_roster):
    ranks = [0, 1, 3, 4, 5]
    for member in api_roster['members']:
        rank = member['rank']
        name = member['character']['name']
        character_id = member['character']['id']

        CurrentUser.objects.filter(name=name).update(rank=rank)
        if rank in ranks:
            Roster.objects.filter(name=name).update_or_create(name=name, rank=rank, character_id=character_id)


def get_guild_roster(request):
    current_user = SocialAccount.objects.filter(user=request.user).first()
    access_token = SocialToken.objects.filter(account=current_user).first()
    header = {
        'Authorization': 'Bearer %s' % access_token,
    }
    response = requests.get(
        'https://eu.api.blizzard.com/data/wow/guild/tarren-mill/a-necessary-evil/roster?namespace=profile-eu&locale=en_US',
        headers=header)
    result = response.json()
    return result

