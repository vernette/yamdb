import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from reviews.models import Category, Comment, Genre, Review, Title, User


class Command(BaseCommand):
    help = 'Загрузка данных в БД из .csv файлов'

    csv_tables = {
        Category: 'category.csv',
        Genre: 'genre.csv',
        User: 'users.csv',
        Title: 'titles.csv',
        Review: 'review.csv',
        Title.genre.through: 'genre_title.csv',
        Comment: 'comments.csv'
    }

    CSV_FILES_DIR = f'{settings.BASE_DIR}/static/data'

    def handle(self, *args, **options):
        for model, filename in self.csv_tables.items():
            with open(
                f'{self.CSV_FILES_DIR}/{filename}',
                'r',
                encoding='utf-8'
            ) as csv_file:
                reader = csv.DictReader(csv_file)
                model.objects.bulk_create(
                    (
                        model(**{'author_id' if key == 'author'
                                 else 'category_id' if key == 'category'
                                 else key: val for key, val in data.items()
                                 }) for data in reader)
                )
                self.stdout.write(
                    f'Обьекты <{model}> '
                    'успешно загружены в базу данных!'
                )
