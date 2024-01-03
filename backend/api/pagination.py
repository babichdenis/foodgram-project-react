from rest_framework.pagination import PageNumberPagination
from rest_framework.settings import api_settings


class CustomPagination(PageNumberPagination):
    """
    Пользовательская пагинация.

    Включает ключ запроса для указания размера страницы.
    """

    page_size_query_param = "limit"
    page_size = api_settings.PAGE_SIZE
