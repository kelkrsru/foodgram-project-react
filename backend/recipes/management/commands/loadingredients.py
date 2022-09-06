import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from recipes.models import Ingredient

DATA_ROOT = os.path.join(settings.BASE_DIR, 'data')


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            with open(os.path.join(DATA_ROOT, 'ingredients.csv'),
                      "r", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    obj, created = Ingredient.objects.get_or_create(
                        name=row[0],
                        measurement_unit=row[1]
                    )
                    if not created:
                        print(f'"Ингредиент {row[0] = }" с единицей измерения '
                              f'"{row[1] = }" уже есть в БД {obj.pk = }')
        except FileNotFoundError:
            raise CommandError(f'Файл ingredients.csv не найден в директории '
                               f'{DATA_ROOT = }')
