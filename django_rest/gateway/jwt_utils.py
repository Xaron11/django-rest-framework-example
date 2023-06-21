from datetime import datetime, timedelta
import random
import string
import jwt


def get_random(length):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def get_access_token(payload, key):
    return jwt.encode(
        {"exp": datetime.now() + timedelta(minutes=5), **payload},
        key, algorithm="HS256"
    )


def get_refresh_token(key):
    return jwt.encode(
        {"exp": datetime.now() + timedelta(days=365), 'data': get_random(16)},
        key, algorithm="HS256"
    )


def get_tokens(payload, key):
    access = get_access_token(payload, key)
    refresh = get_refresh_token(key)
    return access, refresh


def verify_token(token, key):
    try:
        decoded_data = jwt.decode(token, key, algorithms=["HS256"])
    except jwt.DecodeError:
        return None

    if datetime.now().timestamp() > decoded_data['exp']:
        return None

    return decoded_data
