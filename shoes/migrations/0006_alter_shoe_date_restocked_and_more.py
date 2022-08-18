# Generated by Django 4.0.6 on 2022-08-18 12:54

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shoes', '0005_alter_shoe_date_restocked_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shoe',
            name='date_restocked',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2022, 8, 18, 13, 53, 59, 515829)),
        ),
        migrations.AlterUniqueTogether(
            name='shoeimage',
            unique_together={('image', 'color')},
        ),
        migrations.AlterUniqueTogether(
            name='shoevariant',
            unique_together={('shoe', 'size', 'color')},
        ),
    ]
