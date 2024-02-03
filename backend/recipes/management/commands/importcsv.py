import csv

from django.core.management import BaseCommand

from recipes.models import Ingredient, Tag

TABLES = (
    (Tag, 'tags.csv'),
    (Ingredient, 'ingredients.csv')
)
fields = (
    ('name', 'color', 'slug'),
    ('name', 'measurement_unit')
)

csv_file_path = './data/'


class Command(BaseCommand):
    help = 'Команда для создания БД на основе имеющихся csv файлов'

    def handle(self, *args, **kwargs):
        print("Старт импорта")
        try:
            for model, csv_f in TABLES:
                with open(
                    f'{csv_file_path}/{csv_f}', encoding='utf-8'
                ) as f:
                    reader = csv.DictReader(f, delimiter=',')
                    for row in reader:
                        if model in fields:
                            row[fields[model][2]] = row.pop(fields[model][0])
                        obj, created = model.objects.get_or_create(**row)
                    if created:
                        print(f'{obj} загружен в таблицу {model.__name__}')
            print("Загрузка данных завершена.")

        except Exception as error:
            print(f"Сбой в работе импорта: {error}.")

        finally:
            print("Завершена работа импорта.")
