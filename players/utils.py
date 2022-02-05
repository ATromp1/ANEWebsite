"""Extract nested values from a JSON tree."""
from players.models import Roster, CurrentUser


def json_extract(obj, key):
    """Recursively fetch values from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    values = extract(obj, arr, key)
    return values


def get_chars_in_roster(current_user_id):
    roster = []
    for character in Roster.objects.all():
        roster.append(character.name)
    user_chars = []
    for character in CurrentUser.objects.filter(account_id=current_user_id):
        user_chars.append(character.name)
    user_chars_in_roster = set(roster).intersection(set(user_chars))
    return user_chars_in_roster