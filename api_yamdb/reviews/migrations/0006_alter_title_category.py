# Generated by Django 3.2 on 2024-03-05 06:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0005_auto_20240305_0944'),
    ]

    operations = [
        migrations.AlterField(
            model_name='title',
            name='category',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='reviews.category', verbose_name='Slug категории'),
        ),
    ]
