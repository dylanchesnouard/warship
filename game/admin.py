from django.contrib import admin
from .models import Grid, Ship, Shot


# Register your models here.
@admin.register(Grid)
class GridAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nb_rows",
        "nb_columns",
        "created_at",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "nb_columns",
                    "nb_rows",
                    "created_at",
                )
            },
        ),
    )
    readonly_fields = ("id", "created_at")


@admin.register(Ship)
class ShipAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "__str__",
        "x",
        "y",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "grid",
                    "ship_size",
                )
            },
        ),
        (
            "Ship location",
            {
                "fields": (
                    "x",
                    "y",
                    "orientation",
                )
            },
        ),
    )
    readonly_fields = ("id",)


@admin.register(Shot)
class ShotAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "x",
        "y",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "grid",
                    "x",
                    "y",
                )
            },
        ),
    )
    readonly_fields = ("id",)
