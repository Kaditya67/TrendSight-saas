from django.db import models
from user.models import User

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
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, related_name="financial_data_sector",null=True, blank=True)  # One-to-one with Sector
    date = models.DateField(null=True,blank=True)
    high = models.FloatField()  # Average high price for the sector
    low = models.FloatField()  # Average low price for the sector
    close = models.FloatField()  # Average close price for the sector
    open = models.FloatField()  # Average open price for the sector
    last_updated = models.DateTimeField(auto_now=True)  # Timestamp when this data was last updated

    def __str__(self):
        return f"Sector Financial Data for {self.sector.name}"


# Aggregated computed metrics for a sector (e.g., average RS, RSI)
class ComputedSectorData(models.Model):
    # One-to-One relationship with the Sector model
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, related_name="computed_sector_data")# One-to-one with Sector
    date = models.DateField(null=True,blank=True)
    rs = models.FloatField(null=True,blank=True)  # Average relative strength (RS) for the sector
    rsi = models.FloatField(null=True,blank=True)  # Average relative strength index (RSI) for the sector
    ema10 = models.FloatField()  # Average EMA (10 days) for the sector
    ema20 = models.FloatField()  # Average EMA (20 days) for the sector
    ema30 = models.FloatField()  # Average EMA (30 days) for the sector
    ema50 = models.FloatField()  # Average EMA (50 days) for the sector
    ema100 = models.FloatField()  # Average EMA (100 days) for the sector
    ema200 = models.FloatField()  # Average EMA (200 days) for the sector
    last_updated = models.DateTimeField(auto_now=True)  # Timestamp when this data was last updated

    def __str__(self):
        return f"Computed Sector Data for {self.sector.name}"

from django.db.models.signals import m2m_changed
from django.dispatch import receiver

class Watchlist(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlists")
    stocks = models.ManyToManyField('Stock', related_name="watchlist_stocks", blank=True)
    sectors = models.ManyToManyField('Sector', related_name="watchlist_sectors", blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    count = models.PositiveIntegerField(default=0)  # New field to store the count of stocks and sectors

    def __str__(self):
        return f"{self.name} Watchlist"
    
    def update_count(self):
        """Update the count of stocks and sectors in the watchlist."""
        self.count = self.stocks.count() + self.sectors.count()

    # Override save method to update the count before saving
    def save(self, *args, **kwargs):
        self.update_count()  # Update count before saving
        super().save(*args, **kwargs)  # Save the watchlist once with the updated count

    class Meta:
        verbose_name = 'Watchlist'
        verbose_name_plural = 'Watchlists'


# Signal to update count when stocks or sectors are added or removed
@receiver(m2m_changed, sender=Watchlist.stocks.through)
@receiver(m2m_changed, sender=Watchlist.sectors.through)
def update_watchlist_count(sender, instance, **kwargs):
    """Updates the count of stocks and sectors when they are added/removed."""
    instance.update_count()  # Update the count field
    instance.save()  # Save the instance after count update

class Portfolio(models.Model):
    """
    Represents a user's portfolio for a specific stock.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="portfolios")
    stock = models.ForeignKey('Stock', on_delete=models.CASCADE, related_name="portfolios")
    last_purchased_date = models.DateField()
    quantity = models.PositiveIntegerField(default=0)
    average_purchase_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.username}'s portfolio: {self.stock.name} - {self.quantity} shares @ {self.average_purchase_price}"


class SellStocks(models.Model):
    """
    Represents a sell transaction for a specific stock by a user.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sales")
    stock = models.ForeignKey('Stock', on_delete=models.CASCADE, related_name="sales")
    quantity = models.PositiveIntegerField()  # Quantity of stock sold
    total_price = models.DecimalField(max_digits=15, decimal_places=2)  # Total price of the sale
    last_sell_date = models.DateField()
    is_profit = models.BooleanField()  # True if sale resulted in a profit, else False
    profit_or_loss = models.DecimalField(max_digits=15, decimal_places=2)  # Amount of profit or loss

    def __str__(self):
        return f"{self.user.username} sold {self.quantity} shares of {self.stock.name} for {self.total_price}"
