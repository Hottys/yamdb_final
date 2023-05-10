import csv

from django.core.management.base import BaseCommand

from reviews.models import Review


class Command(BaseCommand):
    help = 'Импорт данных из csv в модель Review'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str)

    def handle(self, *args, **options):
        file_path = options['path']
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                Review.objects.create(
                    id=row[0],
                    title_id=row[1],
                    text=row[2],
                    author_id=row[3],
                    score=row[4],
                    pub_date=row[5]
                )
