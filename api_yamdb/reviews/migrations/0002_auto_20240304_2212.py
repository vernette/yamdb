# Generated by Django 3.2 on 2024-03-04 19:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='titles',
            name='category',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='reviews.categories', verbose_name='Slug категории'),
        ),
        migrations.RemoveField(
            model_name='titles',
            name='genre_name',
        ),
        migrations.AddField(
            model_name='titles',
            name='genre_name',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='reviews.genres', verbose_name='Slug жанра'),
        ),
    ]
