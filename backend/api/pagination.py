from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """
    Пользовательская пагинация.

    Включает ключ запроса для указания размера страницы.
    """

    page_size_query_param = "limit"
    page_size = 6
