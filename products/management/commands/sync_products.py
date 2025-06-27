import requests
from django.core.management.base import BaseCommand
from products.models import Product 
from products.views import get_or_create_category,get_or_create_brand
class Command(BaseCommand):
    help = 'Sync products from external APIs'

    
    def handle(self, *args, **kwargs):
        
        def get_nested(data, path):
            for key in path.split('.'):
                data = data.get(key) if isinstance(data, dict) else None
            return data
        servers = [
            {
                'name': 'fakestoreapi',
                'url': 'https://fakestoreapi.com/products',
                'auth': {},
                'id_field': 'id',
                'name_field': 'title',
                'price_field': 'price',
                'discount_field':'discount',
                'description_field': 'description',
                'category_field': 'category',
                'brand_field':'brand',
                'model_field':'model',
                'color_field':'color',
                'images_field': 'image',
                'stock_field':'stock',
                'tags_field':'tags',
                'popular_field':'popular',
            },
            {
                'name': 'escuelajs',
                'url': 'https://api.escuelajs.co/api/v1/products',
                'auth': {},
                'id_field': 'id',
                'name_field': 'title',
                'price_field': 'price',
                'discount_field':'discount',
                'description_field': 'description',
                'category_field': 'category.name',
                'brand_field':'brand',
                'model_field':'model',
                'color_field':'color',
                'images_field': 'images', 
                'stock_field':'stock',
                'tags_field':'tags',
                'popular_field':'popular',
            },
            {
                'name': 'dummyjson',
                'url': 'https://dummyjson.com/products?limit=194',
                'auth': {},
                'id_field': 'id',
                'name_field': 'title',
                'price_field': 'price',
                'discount_field':'discountPercentage',
                'description_field': 'description',
                'category_field': 'category',
                'brand_field':'brand',
                'model_field':'model',
                'color_field':'color',
                'images_field': 'images',
                'stock_field':'stock',
                'tags_field':'tags',
                'popular_field':'popular',
            },
            {
                'name': 'fakestoreapi.in',
                'url': 'https://fakestoreapi.in/api/products?limit=150',
                'auth': {},
                'id_field': 'id',
                'name_field': 'title',
                'price_field': 'price',
                'discount_field':'discount',
                'description_field': 'description',
                'category_field': 'category',
                'brand_field':'brand',
                'model_field':'model',
                'color_field':'color',
                'images_field': 'image',
                'stock_field':'stock',
                'tags_field':'tags',
                'popular_field':'popular',
            },
    ]
    
        for server in servers:
            try:
                response = requests.get(server['url'], **server['auth'])
                response.raise_for_status()
                
                response_data = response.json()
                products = response_data.get('products') if isinstance(response_data, dict) else response_data
                
                for i,product_data in enumerate(products, start=1):
                    external_id = str(product_data[server['id_field']])

                    category_name = get_nested(product_data, server.get('category_field'))
                    category_obj = get_or_create_category(category_name)
                    
                    brand_name = get_nested(product_data, server.get('brand_field'))
                    brand_obj = get_or_create_brand(brand_name)

                    raw_images = product_data.get(server.get('images_field', ''), [])
                    if isinstance(raw_images, list):
                        images = raw_images
                    elif isinstance(raw_images, str) and raw_images:
                        images = [raw_images]
                    else:
                        images = []
                    first_image = images[0] if images else ''

                    defaults = {
                        'external_id': external_id,
                        'source_server': server['name'],
                        'name': product_data.get(server['name_field']),
                        'price': product_data.get(server['price_field']),
                        'model': product_data.get(server['model_field'], ''),
                        'color': product_data.get(server['color_field'], ''),
                        'is_popular': product_data.get(server['popular_field'], False),
                        'discount':product_data.get(server['discount_field']),
                        'description': product_data.get(server['description_field']),
                        'category': category_obj,
                        'brand': brand_obj,
                        'image_url': first_image,
                        'stock':product_data.get(server['stock_field'], 10),
                    }
                    product,created =Product.objects.update_or_create(
                        external_id=external_id,
                        source_server=server['name'],
                        defaults=defaults
                    )
                    product.tags.add(*product_data.get(server.get('tags_field')) or [])
                action = "Created" if created else "Updated"
                self.stdout.write(self.style.SUCCESS(f'Successfully {action}: ({i}) products from {server["name"]}'))
            except requests.RequestException as e:
                self.stdout.write(self.style.ERROR(f'Failed to sync from {server["name"]}: {e}'))
            except (KeyError, ValueError, IndexError) as e:
                self.stdout.write(self.style.ERROR(f'Error processing data from {server["name"]}: {e}'))