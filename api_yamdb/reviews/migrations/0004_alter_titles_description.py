# Generated by Django 3.2 on 2024-03-04 19:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0003_auto_20240304_2216'),
    ]

    operations = [
        migrations.AlterField(
            model_name='titles',
            name='description',
            field=models.TextField(null=True, verbose_name='Описание'),
        ),
    ]
