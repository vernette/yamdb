# Generated by Django 3.2 on 2024-03-10 11:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0003_auto_20240309_1820'),
    ]

    operations = [
        migrations.RenameField(
            model_name='title',
            old_name='genre_name',
            new_name='genre',
        ),
    ]
