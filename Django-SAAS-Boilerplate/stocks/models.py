from django.db import models

# Store sector data manually
class Sector(models.Model):
    # Unique identifier for each sector
    id = models.AutoField(primary_key=True)  # Auto-incremented primary key
    name = models.CharField(max_length=255)  # Name of the sector (e.g., Technology)
    symbol = models.CharField(max_length=255, unique=True, null=True, blank=True)  # Symbol for the sector (e.g., TECH)
    description = models.TextField(blank=True, null=True)  # Optional description for the sector
    last_updated = models.DateTimeField(auto_now=True)  # Timestamp when the sector data was last updated

    def __str__(self):
        return self.name


# Store stock data manually
class Stock(models.Model):
    # Unique identifier for each stock
    id = models.AutoField(primary_key=True)  # Auto-incremented primary key
    symbol = models.CharField(max_length=255, unique=True)  # Stock symbol (e.g., AAPL, MSFT)
    name = models.CharField(max_length=255)  # Name of the stock
    sectors = models.ManyToManyField(Sector, related_name="stocks", blank=True)
    last_updated = models.DateTimeField(auto_now=True)  # Timestamp when the stock data was last updated

    def __str__(self):
        return self.symbol


# Fetch stock data from external sources like Yahoo Finance
class FinancialStockData(models.Model):
    # One-to-One relationship with the Stock model
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name="financial_data", null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    high = models.FloatField()  # Daily high price
    low = models.FloatField()  # Daily low price
    close = models.FloatField()  # Closing price
    open = models.FloatField()  # Opening price
    volume = models.FloatField()  # Trading volume
    last_updated = models.DateTimeField(auto_now=True)  # Timestamp for when this data was last updated

    class Meta:
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['stock']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['stock', 'date'], name='unique_stock_date'),  # Ensure unique records
        ]


    def __str__(self):
        return f"Financial Data for {self.stock.symbol}"
    
class PrevVolumes(models.Model):
    # One-to-One relationship with the Stock model
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name="prev_volumes", null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    volume20 = models.CharField(max_length=255,blank=True,null=True) 
    volume50 = models.CharField(max_length=255,blank=True,null=True)  

    def __str__(self):
        return f"Prev Volumes for {self.stock.symbol}"

# Calculate computed metrics for each stock independently
class ComputedStockData(models.Model):
    # One-to-One relationship with the Stock model
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name="computed_data")  # One-to-one with Stock
    date = models.DateField(null=True,blank=True)  # Date for which the data is computed
    rs = models.FloatField(blank=True,null=True)  # Relative Strength value
    rsi = models.FloatField(blank=True,null=True)  # Relative Strength Index
    ema10 = models.FloatField()  # Exponential Moving Average (10 days)
    ema20 = models.FloatField()  # Exponential Moving Average (20 days)
    ema30 = models.FloatField()  # Exponential Moving Average (30 days)
    ema50 = models.FloatField()  # Exponential Moving Average (50 days)
    ema100 = models.FloatField()  # Exponential Moving Average (100 days)
    ema200 = models.FloatField()  # Exponential Moving Average (200 days)
    volume20 = models.CharField(max_length=255,blank=True,null=True)  # Volume over 20 days (can be a string to represent trend, etc.)
    volume50 = models.CharField(max_length=255,blank=True,null=True)  # Volume over 50 days (same as above)
    last_updated = models.DateTimeField(auto_now=True)  # Timestamp when this data was last updated

    class Meta:
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['stock']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['stock', 'date'], name='unique_stockIndicator_date'),
        ]

    def __str__(self):
        return f"Computed Data for {self.stock.symbol}"


# Aggregated sector data (e.g., averages for a given sector)
class SectorFinancialData(models.Model):
    # One-to-One relationship with the Sector model
    sector = models.OneToOneField(Sector, on_delete=models.CASCADE, primary_key=True, related_name="financial_data")  # One-to-one with Sector
    avg_high = models.FloatField()  # Average high price for the sector
    avg_low = models.FloatField()  # Average low price for the sector
    avg_close = models.FloatField()  # Average close price for the sector
    avg_open = models.FloatField()  # Average open price for the sector
    total_volume = models.IntegerField()  # Total trading volume for the sector
    last_updated = models.DateTimeField(auto_now=True)  # Timestamp when this data was last updated

    def __str__(self):
        return f"Sector Financial Data for {self.sector.name}"


# Aggregated computed metrics for a sector (e.g., average RS, RSI)
class ComputedSectorData(models.Model):
    # One-to-One relationship with the Sector model
    sector = models.OneToOneField(Sector, on_delete=models.CASCADE, primary_key=True, related_name="computed_data")  # One-to-one with Sector
    avg_rs = models.FloatField()  # Average relative strength (RS) for the sector
    avg_rsi = models.FloatField()  # Average relative strength index (RSI) for the sector
    avg_ema10 = models.FloatField()  # Average EMA (10 days) for the sector
    avg_ema20 = models.FloatField()  # Average EMA (20 days) for the sector
    avg_ema30 = models.FloatField()  # Average EMA (30 days) for the sector
    avg_ema50 = models.FloatField()  # Average EMA (50 days) for the sector
    avg_ema100 = models.FloatField()  # Average EMA (100 days) for the sector
    avg_ema200 = models.FloatField()  # Average EMA (200 days) for the sector
    volume_trend = models.CharField(max_length=255)  # Trend of the volume in the sector (e.g., 'up', 'down', 'steady')
    last_updated = models.DateTimeField(auto_now=True)  # Timestamp when this data was last updated

    def __str__(self):
        return f"Computed Sector Data for {self.sector.name}"
