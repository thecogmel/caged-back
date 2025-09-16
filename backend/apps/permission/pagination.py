from rest_framework import pagination

class PermissionPagination(pagination.PageNumberPagination):
    page_size = 99999999
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'p'
