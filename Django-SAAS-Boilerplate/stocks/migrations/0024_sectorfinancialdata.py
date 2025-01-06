# Generated by Django 4.2.11 on 2025-01-06 13:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0023_delete_sectorfinancialdata'),
    ]

    operations = [
        migrations.CreateModel(
            name='SectorFinancialData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, null=True)),
                ('high', models.FloatField()),
                ('low', models.FloatField()),
                ('close', models.FloatField()),
                ('open', models.FloatField()),
                ('volume', models.IntegerField()),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('sector', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='financial_data_sector', to='stocks.sector')),
            ],
        ),
    ]
