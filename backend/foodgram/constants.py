class Constants:

    REGEX: str = r"^[\w.@+-]+$"  # проверка слагов
    REGEXCOLOR: str = r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"  # проверка HEX
    MAX_CHAR_LENGTH: int = 200
    MAX_COLOR_LENGTH: int = 7
    MAX_EMAIL_LENGTH: int = 254
    MAX_USERNAME_LENGTH: int = 150
    STRLENGTH: int = 25
    MAX_PAGE_SIZE: int = 30
    PAGINATE_SIZE: int = 6
    MIN_INGREDIENT_AMOUNT: int = 1
    MIN_COOKING_TIME: int = 1
    MAX_COOKING_TIME: int = 1000
    MIN_AMOUNT: int = 1
    MAX_AMOUNT: int = 10000
