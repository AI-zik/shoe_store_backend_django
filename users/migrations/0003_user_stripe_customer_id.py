# Generated by Django 4.0.6 on 2022-07-23 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_address_user_city_user_country_user_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='stripe_customer_id',
            field=models.CharField(default='allsooo', max_length=120),
            preserve_default=False,
        ),
    ]