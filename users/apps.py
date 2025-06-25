from django.apps import AppConfig
from django.contrib import admin

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        import users.signals
        admin.site.site_header = "E-commerce administration"
        admin.site.site_title = "Admin Panel"
        admin.site.index_title = "E-commerce"
