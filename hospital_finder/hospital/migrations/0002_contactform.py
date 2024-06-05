# Generated by Django 4.2.13 on 2024-06-05 15:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("hospital", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ContactForm",
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
                ("name", models.CharField(max_length=100)),
                ("email", models.EmailField(max_length=254)),
                ("message", models.TextField()),
            ],
        ),
    ]
