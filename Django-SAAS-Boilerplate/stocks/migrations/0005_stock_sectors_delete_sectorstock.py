# Generated by Django 4.2.11 on 2024-12-31 06:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0004_alter_sector_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='sectors',
            field=models.ManyToManyField(related_name='stocks', to='stocks.sector'),
        ),
        migrations.DeleteModel(
            name='SectorStock',
        ),
    ]
