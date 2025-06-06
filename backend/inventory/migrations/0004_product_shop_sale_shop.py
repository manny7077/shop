# Generated by Django 5.1.5 on 2025-04-07 03:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_shop'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='shop',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='inventory.shop'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sale',
            name='shop',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='sales', to='inventory.shop'),
            preserve_default=False,
        ),
    ]
