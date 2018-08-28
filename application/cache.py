
import boto3
import datetime
import json
import os

# In minutes, cache recipe list for this long
CACHE_TTL = 30

class Data():
    def __init__(self, s3_bucket, s3_key):
        self.s3 = boto3.resource('s3')
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key
        self.data = None

        self._get_recipes()

    def _load_data(self):
        if not self.data or self.refresh_time < datetime.datetime.utcnow():
            self.data = json.load(self.s3.Object(self.s3_bucket, self.s3_key).get().get('Body'))
            print('Refreshed data')
            self.refresh_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=CACHE_TTL)

    def _get_categories(self):
        self._load_data()
        return self.data['categories']

    def _get_recipes(self):
        self._load_data()
        return self.data['recipes']

    def all(self):
        return self._get_recipes()

    def single(self, title):
        recipes = self._get_recipes()
        if title in recipes:
            return recipes[title]

        return False

    def categories(self):
        return self._get_categories()

    def in_category(self, category):
        categories = self._get_categories()
        if category in categories:
            return categories[category]

        return False

recipes = Data(
    os.environ.get('S3_BUCKET', 'not-your-grandmas-recipe-box'),
    os.environ.get('S3_KEY', 'recipe-box-conversion.json')
)
