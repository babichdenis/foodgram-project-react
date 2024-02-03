from foodgram.constants import Constants
from rest_framework.pagination import PageNumberPagination


class Pagination(PageNumberPagination):
    """Кастомная пагинация."""

    page_size = Constants.PAGINATE_SIZE
    page_size_query_param = "limit"
    max_page_size = Constants.MAX_PAGE_SIZE
