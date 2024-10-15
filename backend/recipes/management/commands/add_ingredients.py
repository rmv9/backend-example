import csv

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import IntegrityError

from recipes.models import Ingredient


class Command(BaseCommand):
    """Ingredients csv loader"""

    def handle(self, *args, **options):
        file_path = settings.BASE_DIR / 'data/ingredients.csv'
        with open(file_path, 'r', encoding='utf-8',) as file:
            try:
                Ingredient.objects.bulk_create(
                    Ingredient(
                        name=row[0],
                        measurement_unit=row[1]
                    )
                    for row in csv.reader(file)
                )
                self.stdout.write(
                    self.style.SUCCESS('Done')
                )
            except IntegrityError:
                self.stdout.write(
                    self.style.ERROR('Failed')
                )
