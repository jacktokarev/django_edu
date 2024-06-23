# Generated by Django 5.0.3 on 2024-05-24 13:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blogapp", "0003_tag"),
    ]

    operations = [
        migrations.CreateModel(
            name="Article",
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
                ("title", models.CharField(max_length=200, verbose_name="Title")),
                ("content", models.TextField(verbose_name="Content")),
                ("pub_date", models.DateTimeField(auto_now_add=True, verbose_name="")),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="blogapp.author",
                        verbose_name="Author",
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="blogapp.category",
                        verbose_name="Category",
                    ),
                ),
                (
                    "tags",
                    models.ManyToManyField(
                        related_name="articles", to="blogapp.tag", verbose_name="Tags"
                    ),
                ),
            ],
        ),
    ]
