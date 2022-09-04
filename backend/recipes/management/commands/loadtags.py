import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from recipes.models import Tag

DATA_ROOT = os.path.join(os.path.dirname(settings.BASE_DIR), 'data')


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            with open(os.path.join(DATA_ROOT, 'tags.csv'),
                      "r", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    obj, created = Tag.objects.get_or_create(
                        name=row[0],
                        slug=row[2],
                        defaults={'color': row[1]}
                    )
                    if not created:
                        print(f'"Таг {row[0] = }" уже есть в БД {obj.pk = }')
        except FileNotFoundError:
            raise CommandError(f'Файл tags.csv не найден в директории '
                               f'{DATA_ROOT = }')
