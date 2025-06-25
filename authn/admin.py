from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.token_blacklist.admin import OutstandingTokenAdmin

def is_token_blacklisted(obj):
    return BlacklistedToken.objects.filter(token=obj).exists()

is_token_blacklisted.short_description = 'Blacklisted'
is_token_blacklisted.boolean = True 

OutstandingTokenAdmin.list_display = ('user', 'jti', 'expires_at', is_token_blacklisted)
