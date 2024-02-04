# Generated by Django 4.2.7 on 2024-02-04 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bood_app", "0003_alter_product_microelements_alter_product_vitamins"),
    ]

    operations = [
        migrations.AlterField(
            model_name="personcard",
            name="target",
            field=models.CharField(
                blank=True,
                choices=[("keep", "Поддержание формы"), ("gain", "Набор веса"), ("lose", "Похудение")],
                default="",
                max_length=4,
                verbose_name="Цель",
            ),
        ),
    ]
