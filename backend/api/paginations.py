from core.constants import PAGE_SIZE
from rest_framework.pagination import PageNumberPagination


class FoodgramPagination(PageNumberPagination):
    """Project pagination"""

    page_size = PAGE_SIZE
    page_size_query_param = 'limit'
