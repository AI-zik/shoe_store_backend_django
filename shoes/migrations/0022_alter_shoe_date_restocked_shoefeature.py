# Generated by Django 4.0.6 on 2022-07-28 14:23

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shoes', '0021_alter_rating_feedback_alter_shoe_date_restocked'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shoe',
            name='date_restocked',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2022, 7, 28, 15, 23, 48, 647962)),
        ),
        migrations.CreateModel(
            name='ShoeFeature',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('feature', models.CharField(max_length=255)),
                ('shoe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shoes.shoe')),
            ],
        ),
    ]