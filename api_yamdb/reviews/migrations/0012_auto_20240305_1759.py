# Generated by Django 3.2 on 2024-03-05 17:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0011_review_title'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='review',
            options={'verbose_name': 'отзыв', 'verbose_name_plural': 'Отзывы'},
        ),
        migrations.RenameField(
            model_name='review',
            old_name='created',
            new_name='pub_date',
        ),
        migrations.AlterField(
            model_name='review',
            name='text',
            field=models.TextField(verbose_name='Текст'),
        ),
    ]
