# Generated by Django 5.0.3 on 2024-05-25 06:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("blogapp", "0005_alter_author_name"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="article",
            options={"verbose_name": "Article"},
        ),
        migrations.AlterModelOptions(
            name="author",
            options={"verbose_name": "Author"},
        ),
        migrations.AlterModelOptions(
            name="category",
            options={"verbose_name": "Category"},
        ),
        migrations.AlterModelOptions(
            name="tag",
            options={"verbose_name": "Tag"},
        ),
    ]
