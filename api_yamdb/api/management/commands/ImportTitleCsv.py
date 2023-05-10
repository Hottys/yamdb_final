import csv

from django.core.management.base import BaseCommand

from reviews.models import Title


class Command(BaseCommand):
    help = 'Импорт данных из csv в модель Title'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str)

    def handle(self, *args, **options):
        file_path = options['path']
        with open(file_path, 'r', encoding='tf-8') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                Title.objects.create(
                    id=row[0],
                    name=row[1],
                    year=row[2],
                    category_id=row[3]
                )
