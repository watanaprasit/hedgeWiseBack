import yfinance as yf
from django.core.management.base import BaseCommand
from main.models import CurrencyData
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Fetch historical currency data for the past 30 hours and store it in the database.'

    def handle(self, *args, **kwargs):
        # Define the currency pairs
        currency_pairs = ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X']
        
        # Calculate the start and end date for the last 30 days (for historical data)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Iterate over each currency pair and fetch data
        for currency_pair in currency_pairs:
            self.fetch_and_save_data(currency_pair, start_date, end_date)

    def fetch_and_save_data(self, currency_pair, start_date, end_date):
        try:
            # Fetch historical data for the last 30 days with 1-day interval
            data = yf.download(currency_pair, start=start_date, end=end_date, interval='1d')

            # Store the data in the database
            for date, row in data.iterrows():
                CurrencyData.objects.create(
                    currency_pair=currency_pair,
                    date=date,
                    open_price=row['Open'],
                    high_price=row['High'],
                    low_price=row['Low'],
                    close_price=row['Close'],
                    volume=row['Volume']
                )
            self.stdout.write(self.style.SUCCESS(f"Successfully fetched and stored data for {currency_pair}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error fetching data for {currency_pair}: {e}"))
