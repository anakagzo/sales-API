# Generated by Django 4.2.3 on 2023-08-10 09:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_healthtips'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='HealthTips',
            new_name='HealthTip',
        ),
        migrations.RenameField(
            model_name='healthtip',
            old_name='body',
            new_name='content',
        ),
    ]
