# Generated by Django 5.0.3 on 2024-05-25 05:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blogapp", "0004_article"),
    ]

    operations = [
        migrations.AlterField(
            model_name="author",
            name="name",
            field=models.CharField(db_index=True, max_length=100, verbose_name="Name"),
        ),
    ]
