# Generated by Django 4.2.11 on 2025-01-11 08:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0032_alter_watchlist_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='watchlist',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
