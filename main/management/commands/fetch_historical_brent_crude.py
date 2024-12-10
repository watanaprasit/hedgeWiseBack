import yfinance as yf
from django.core.management.base import BaseCommand
from main.models import BrentCrudeData
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_DOWN

class Command(BaseCommand):
    help = 'Fetch historical Brent Crude data for the past 30 days and store it in the database.'

    def handle(self, *args, **kwargs):
        # Define the Brent Crude symbol
        symbol = 'BZ=F'  # Symbol for Brent Crude on Yahoo Finance
        
        # Calculate the start and end date for the last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Fetch data
        self.fetch_and_save_data(symbol, start_date, end_date)

    def fetch_and_save_data(self, symbol, start_date, end_date):
        try:
            # Fetch historical data for the last 30 days with 1-day interval
            data = yf.download(symbol, start=start_date, end=end_date, interval='1d')

            # Store the data in the database
            for date, row in data.iterrows():
                # Make the datetime aware
                aware_date = timezone.make_aware(date)
                
                # Convert the closing price to a scalar value and then to Decimal
                price = Decimal(row['Close'].item()).quantize(Decimal('0.001'), rounding=ROUND_DOWN)

                # Save to the database
                BrentCrudeData.objects.create(
                    date=aware_date,
                    price=price
                )

            self.stdout.write(self.style.SUCCESS(f"Successfully fetched and stored data for {symbol}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error fetching data for {symbol}: {e}"))


