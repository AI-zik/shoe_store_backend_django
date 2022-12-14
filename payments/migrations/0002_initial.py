# Generated by Django 4.0.6 on 2022-08-10 13:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('payments', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shoes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='purchase',
            name='shoe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shoes.shoevariant'),
        ),
        migrations.AddField(
            model_name='purchase',
            name='transaction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='payments.transaction'),
        ),
        migrations.AlterUniqueTogether(
            name='purchase',
            unique_together={('transaction', 'shoe')},
        ),
    ]
