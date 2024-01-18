# Generated by Django 4.2.7 on 2023-12-08 17:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("bood_app", "0002_productcategory_alter_faq_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="microelements",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="product",
                to="bood_app.microelement",
                verbose_name="Микроэлементы",
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="vitamins",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="product",
                to="bood_app.vitamin",
                verbose_name="Витамины",
            ),
        ),
    ]
