from rest_framework.pagination import PageNumberPagination


class PageLimitPagination(PageNumberPagination):
    """PageNumberPagination with limit."""
    page_size_query_param = 'limit'
