from django.db import models

class FStockData(models.Model):
    id = models.CharField(max_length=255, primary_key=True)  # Primary Key
    symbol = models.CharField(max_length=255)  # Stock symbol (e.g., TATAMOTORS)
    sector_id = models.CharField(max_length=255)  # Foreign Key (can link to Sector model)
    high = models.IntegerField()  # Daily high price
    low = models.IntegerField()  # Daily low price
    close = models.IntegerField()  # Closing price
    open = models.IntegerField()  # Opening price
    volume = models.IntegerField()  # Daily trading volume
    last_updated = models.DateTimeField(auto_now=True)  # Auto update timestamp
    
    def __str__(self):
        return self.symbol


class CStockData(models.Model):
    id = models.OneToOneField(FStockData, on_delete=models.CASCADE, primary_key=True)  # Link to FStockData
    rs = models.IntegerField()  # Relative Strength value
    rsi = models.IntegerField()  # Relative Strength Index
    ema10 = models.IntegerField()  # Exponential Moving Average (10 days)
    ema20 = models.IntegerField()  # Exponential Moving Average (20 days)
    ema30 = models.IntegerField()  # Exponential Moving Average (30 days)
    ema50 = models.IntegerField()  # Exponential Moving Average (50 days)
    ema100 = models.IntegerField()  # Exponential Moving Average (100 days)
    ema200 = models.IntegerField()  # Exponential Moving Average (200 days)
    last_updated = models.DateTimeField(auto_now=True)  # Auto update timestamp
    
    def __str__(self):
        return f"Computed Data for {self.id.symbol}"
