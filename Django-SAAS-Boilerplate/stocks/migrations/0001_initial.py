# Generated by Django 4.2.11 on 2024-12-28 20:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FStockData',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('symbol', models.CharField(max_length=255)),
                ('sector_id', models.CharField(max_length=255)),
                ('high', models.IntegerField()),
                ('low', models.IntegerField()),
                ('close', models.IntegerField()),
                ('open', models.IntegerField()),
                ('volume', models.IntegerField()),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='CStockData',
            fields=[
                ('id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='stocks.fstockdata')),
                ('rs', models.IntegerField()),
                ('rsi', models.IntegerField()),
                ('ema10', models.IntegerField()),
                ('ema20', models.IntegerField()),
                ('ema30', models.IntegerField()),
                ('ema50', models.IntegerField()),
                ('ema100', models.IntegerField()),
                ('ema200', models.IntegerField()),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]