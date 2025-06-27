from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.response import Response
import math

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        self.request = request
        self.show_all = request.query_params.get('all', 'false').lower() == 'true'
        if self.show_all:
            self.count = len(queryset)
            return list(queryset)
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        if getattr(self, 'show_all', False):
            return Response({
                'count': self.count,
                'current_count': len(data),
                'next': None,
                'previous': None,
                'page': 1,
                'total_pages': 1,
                'results': data
            })

        return Response({
            'count': self.page.paginator.count,
            'current_count': len(data),
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page': self.page.number,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })

class CustomLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 30
    max_limit = 100 

    def get_paginated_response(self, data):
        total_pages = math.ceil(self.count / self.limit) if self.limit else 1
        current_page = math.floor(self.offset / self.limit) + 1 if self.limit else 1

        return Response({
            'count': self.count,
            'current_count': len(data),
            'page': current_page,
            'total_pages': total_pages,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })