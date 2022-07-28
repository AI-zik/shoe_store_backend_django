from rest_framework_simplejwt.tokens import RefreshToken

def float_or_none(value):
    number = ""
    try:
        number = float(value)
    except:
        number = None
    return number

def get_user_tokens(user):

    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }