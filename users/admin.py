from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    readonly_fields = ['user_username','user_email', 'user_first_name', 'user_last_name', 'created_at', 'updated_at',]
    list_display = ['user_username', 'user_email', 'phone', 'city', 'country']
    list_filter = ['country', 'city','created_at', 'updated_at']
    search_fields = ['user__username', 'user__email', 'phone', 'city']
    
    def get_fieldsets(self, request, obj=None):
        user_fields = ['user_email', 'user_first_name', 'user_last_name', 'created_at', 'updated_at',]
        if request.user.is_superuser:
            user_fields.insert(0, 'user')
        return (
            ('User Details', {'fields': user_fields}),
            ('Address', {'fields': ('phone', 'address', 'postal_code', 'city', 'country')}),
        )

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('user')
        if request.user.is_superuser:
            return qs
        return qs.filter(user__is_staff=False, user__is_superuser=False)

    def user_username(self, obj):
        return obj.user.username
    user_username.short_description = 'Username'

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'

    def user_first_name(self, obj):
        return obj.user.first_name
    user_first_name.short_description = 'First Name'

    def user_last_name(self, obj):
        return obj.user.last_name
    user_last_name.short_description = 'Last Name'