# Generated by Django 4.1.3 on 2022-11-24 17:04

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Grid",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "nb_columns",
                    models.PositiveSmallIntegerField(
                        default=8,
                        validators=[django.core.validators.MinValueValidator(8)],
                        verbose_name="Number of columns",
                    ),
                ),
                (
                    "nb_rows",
                    models.PositiveSmallIntegerField(
                        default=8,
                        validators=[django.core.validators.MinValueValidator(8)],
                        verbose_name="Number of rows",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Grid",
                "verbose_name_plural": "Grids",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Ship",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("x", models.PositiveSmallIntegerField(default=0)),
                ("y", models.PositiveSmallIntegerField(default=0)),
                (
                    "orientation",
                    models.CharField(
                        choices=[("H", "Horizontal"), ("V", "Vertical")],
                        default="H",
                        max_length=1,
                    ),
                ),
                (
                    "ship_size",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (4, "Cruiser"),
                            (3, "Escortship"),
                            (2, "Torpedoboat"),
                            (1, "Submarine"),
                        ],
                        default=1,
                    ),
                ),
                (
                    "grid",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ships",
                        to="game.grid",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ship",
                "verbose_name_plural": "Ships",
            },
        ),
        migrations.CreateModel(
            name="Shot",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "x",
                    models.PositiveSmallIntegerField(
                        default=1,
                        validators=[django.core.validators.MinValueValidator(1)],
                    ),
                ),
                (
                    "y",
                    models.PositiveSmallIntegerField(
                        default=1,
                        validators=[django.core.validators.MinValueValidator(1)],
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "grid",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="shots",
                        to="game.grid",
                    ),
                ),
            ],
            options={
                "verbose_name": "Shot",
                "verbose_name_plural": "Shots",
                "ordering": ["-created_at"],
                "unique_together": {("grid", "x", "y")},
            },
        ),
    ]