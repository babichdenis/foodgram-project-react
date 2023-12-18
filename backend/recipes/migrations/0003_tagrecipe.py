# Generated by Django 4.2.8 on 2023-12-18 15:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("recipes", "0002_ingredientrecipe_recipe_ingredientrecipe_recipe"),
    ]

    operations = [
        migrations.CreateModel(
            name="TagRecipe",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "recipe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="recipe_tags",
                        to="recipes.recipe",
                    ),
                ),
                (
                    "tag",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="recipe_tags",
                        to="recipes.tag",
                    ),
                ),
            ],
        ),
    ]