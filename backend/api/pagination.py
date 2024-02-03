from foodgram.constants import MAX_PAGE_SIZE, PAGINATE_SIZE
from rest_framework.pagination import PageNumberPagination


class Pagination(PageNumberPagination):
    """Кастомная пагинация."""

    page_size = PAGINATE_SIZE
    page_size_query_param = "limit"
    max_page_size = MAX_PAGE_SIZE
