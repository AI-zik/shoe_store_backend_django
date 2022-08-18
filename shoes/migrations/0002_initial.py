# Generated by Django 4.0.6 on 2022-08-10 13:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shoes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='rating',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='category',
            name='parent',
            field=models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='shoes.category'),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='shoe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='in_cart', to='shoes.shoevariant'),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopping_cart', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='shoevariant',
            unique_together={('shoe', 'shoe', 'color')},
        ),
        migrations.AlterUniqueTogether(
            name='shoecategory',
            unique_together={('category', 'shoe')},
        ),
        migrations.AlterUniqueTogether(
            name='rating',
            unique_together={('user', 'shoe')},
        ),
    ]