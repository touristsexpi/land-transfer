# Generated by Django 4.2.6 on 2023-11-10 09:19

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='file_path',
            field=models.FileField(blank=True, null=True, upload_to=users.models.upload_to),
        ),
    ]
