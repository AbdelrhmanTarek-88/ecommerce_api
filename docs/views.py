import json
from django.shortcuts import render
from django.conf import settings
import os

def api_docs_view(request):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, 'endpoints_test.json')

    with open(json_path, 'r', encoding='utf-8') as f:
        full_data = json.load(f)
        description = full_data.get("description", "Browse all available API endpoints below.")
        version = full_data.get("version", "0.v")
        last_updated = full_data.get("last_updated", "2025-06-05")
        author = full_data.get("author", "Abdelrhman Tarek")
        raw_data = full_data["THIS FILE TO TEST ALL ENDPOINTS"]

    cleaned_data = {}

    for module, endpoints in raw_data.items():
        cleaned_data[module] = []
        for name, details in endpoints.items():
            response = details.get('Expected Response', {})
            cleaned_data[module].append({
                'name': name,
                'api': details.get('API'),
                'method': details.get('Method'),
                'auth': details.get('Authorization'),
                'headers': details.get('Headers'),
                'querys': details.get('Query Parameters'),
                'body': details.get('Body') if details.get('Body') not in [{}] else 'No Parameters',
                'response_status': response.get('status') if response.get('status') not in [{}] else 'No Status',
                'response_data': response.get('data') if response.get('data') not in [{}] else 'No Parameters',
            })
    return render(request, 'api_docs.html', {
        'api_data': cleaned_data,
        'description': description,
        'version':version,
        'last_updated':last_updated,
        'author':author,
        'BASE_URL': settings.BASE_URL
    })

def custom_500_view(request):
    return render(request, '500.html', status=500)

def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

def custom_403_view(request, exception):
    return render(request, '403.html', status=403)

def custom_401_view(request):
    return render(request, '401.html', status=401)

def custom_400_view(request, exception):
    return render(request, '400.html', status=400)