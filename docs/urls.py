from django.urls import path
from .views import api_docs_view

app_name = 'docs'

urlpatterns = [
    path('', api_docs_view, name='api-docs'),
]
