# Generated by Django 4.2.11 on 2024-12-31 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0012_alter_computedstockdata_rs'),
    ]

    operations = [
        migrations.AddField(
            model_name='computedstockdata',
            name='date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
