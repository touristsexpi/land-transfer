# Generated by Django 4.2.6 on 2023-12-12 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_inspectionimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inspectionimage',
            name='image',
            field=models.ImageField(upload_to='inspections/'),
        ),
    ]
