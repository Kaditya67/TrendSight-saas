# Generated by Django 4.2.11 on 2024-12-31 06:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0003_sector_symbol'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sector',
            name='name',
            field=models.CharField(max_length=255),
        ),
    ]
