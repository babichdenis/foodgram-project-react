# Generated by Django 3.2.16 on 2024-01-22 13:49

import colorfield.fields
import django.core.validators
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_favoritrecipe_date_added'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=colorfield.fields.ColorField(default='#FF0000', image_field=None, max_length=7, samples=None, validators=[django.core.validators.RegexValidator(message='Введите правильный цвет в формате HEX', regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')], verbose_name='Цветовой HEX-код'),
        ),
    ]