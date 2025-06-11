import requests
from django.core.management.base import BaseCommand
from products.models import Product, Category

class Command(BaseCommand):
    help = 'Sync products from external APIs'

    def handle(self, *args, **kwargs):
        servers = [
            {
                'name': 'fakestoreapi',
                'url': 'https://fakestoreapi.com/products',
                'auth': {},
                'id_field': 'id',
                'name_field': 'title',
                'price_field': 'price',
                'description_field': 'description',
                'category_field': 'category',
                'image_field': 'image',
                'num_reviews_field': 'rating.count',
                'stock':10,
            },
            {
                'name': 'escuelajs',
                'url': 'https://api.escuelajs.co/api/v1/products',
                'auth': {},
                'id_field': 'id',
                'name_field': 'title',
                'price_field': 'price',
                'description_field': 'description',
                'category_field': 'category.name',
                'image_field': 'images',
                'images_field': 'images', 
                'slug_field': 'slug',
            },
        ]

        for server in servers:
            try:
                response = requests.get(server['url'], **server['auth'])
                response.raise_for_status()
                products = response.json()

                for product_data in products:
                    external_id = str(product_data[server['id_field']])
                    price = float(product_data[server['price_field']])
                    
                    category_field_path = server.get('category_field')
                    keys = category_field_path.split('.')
                    value = product_data
                    for key in keys:
                        value = value.get(key) if isinstance(value, dict) else None
                    category_name = value
                    category_obj, _ = Category.objects.get_or_create(name=category_name)

                    images = product_data.get(server['images_field'], []) if 'images_field' in server and server['images_field'] in product_data else []
                    if not images and 'image_field' in server:
                        single_image = product_data.get(server['image_field'], '')
                        images = [single_image] if single_image else []
                    first_image = images[0] if images else ''

                    defaults = {
                        'external_id': external_id,
                        'source_server': server['name'],
                        'name': product_data.get(server['name_field']),
                        'price': price,
                        'description': product_data.get(server.get('description_field')),
                        'category': category_obj,
                        'image_field': None,
                        'image_url': first_image,
                        'slug': product_data.get(server.get('slug_field')),
                        'stock':10
                    }
                    Product.objects.update_or_create(
                        external_id=external_id,
                        source_server=server['name'],
                        defaults=defaults
                    )
                self.stdout.write(self.style.SUCCESS(f'Successfully synced products from {server["name"]}'))
            except requests.RequestException as e:
                self.stdout.write(self.style.ERROR(f'Failed to sync from {server["name"]}: {e}'))
            except (KeyError, ValueError, IndexError) as e:
                self.stdout.write(self.style.ERROR(f'Error processing data from {server["name"]}: {e}'))