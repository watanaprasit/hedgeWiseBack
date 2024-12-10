from django.core.management.base import BaseCommand
import requests
from main.models import GeopoliticalNews
from dotenv import load_dotenv
import os

class Command(BaseCommand):
    help = 'Fetch latest geopolitical news from the News API'

    def handle(self, *args, **kwargs):
        url = "https://newsapi.org/v2/everything"
        api_key = os.getenv('NEWSAPI_KEY')
        params = {
            "q": "Syria AND war",
            "apiKey": api_key,
            "pageSize": 20,
            "sortBy": "publishedAt",
            "language": "en",
        }

        response = requests.get(url, params=params)
        
        print(response.status_code)

        if response.status_code == 200:
            articles = response.json().get('articles', [])
            for article in articles:
                GeopoliticalNews.objects.create(
                    title=article['title'],
                    description=article['description'],
                    url=article['url'],
                    published_at=article['publishedAt'],
                    source=article['source']['name']
                )
            self.stdout.write(self.style.SUCCESS("Successfully fetched and saved news articles"))
        else:
            self.stdout.write(self.style.ERROR("Failed to fetch news"))
