# Generated by Django 4.2.3 on 2023-08-04 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_product_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='unit_code',
            field=models.CharField(default='sachet', max_length=10),
            preserve_default=False,
        ),
    ]
