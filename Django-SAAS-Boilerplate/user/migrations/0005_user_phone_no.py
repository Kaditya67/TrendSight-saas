# Generated by Django 4.2.11 on 2025-01-03 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_alter_user_options_alter_user_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='phone_no',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
