# Generated by Django 5.2.1 on 2025-06-25 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='discount_end',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='discount_start',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
