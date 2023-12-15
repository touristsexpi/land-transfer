# Generated by Django 4.2.6 on 2023-11-17 05:48

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_transaction_file_path'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='area',
            field=models.DecimalField(decimal_places=3, max_digits=9, validators=[users.models.validate_positive]),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='purchase_price',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[users.models.validate_positive]),
        ),
    ]
