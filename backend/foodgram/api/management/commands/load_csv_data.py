import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):

    help = 'Загрузка данных об ингредиентах из CSV-файла в базу данных'

    def handle(self, *args, **options):

        file_path = (
            Path(settings.CSV_FILES_DIR) / 'ingredients.csv'
        )
        with open(
            file_path, 'r', encoding='utf-8'
        ) as csv_file:
            csv_reader = csv.reader(csv_file)
            ingredients_to_create = []
            for row in csv_reader:
                if len(row) == 2:
                    name, measurement_unit = row
                    ingredient, created = Ingredient.objects.get_or_create(
                        name=name,
                        measurement_unit=measurement_unit
                    )
                    if created:
                        ingredients_to_create.append(ingredient)
            Ingredient.objects.bulk_create(ingredients_to_create)

        self.stdout.write(
            self.style.SUCCESS(
                'Успешно загружены данные об ингредиентах из CSV-файла'
            )
        )
