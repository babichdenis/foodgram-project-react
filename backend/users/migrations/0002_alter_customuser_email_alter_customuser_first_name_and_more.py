# Generated by Django 4.2.8 on 2023-12-18 21:23

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="email",
            field=models.EmailField(
                max_length=254, unique=True, verbose_name="email address"
            ),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="first_name",
            field=models.CharField(max_length=150, verbose_name="Имя"),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="last_name",
            field=models.CharField(max_length=150, verbose_name="Фамилия"),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="password",
            field=models.CharField(
                max_length=150,
                validators=[
                    django.core.validators.RegexValidator(
                        message="Недопустимый символ", regex="^[\\w.@+-]+$"
                    )
                ],
                verbose_name="Пароль",
            ),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="username",
            field=models.CharField(
                max_length=150,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        message="Недопустимый символ", regex="^[\\w.@+-]+$"
                    )
                ],
                verbose_name="Логин",
            ),
        ),
    ]
