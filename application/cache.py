
import boto3
import datetime
import json
import os

# In minutes, cache recipe list for this long
CACHE_TTL = 30

class Recipes():
    def __init__(self, s3_bucket, s3_key):
        self.s3 = boto3.resource('s3')
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key
        self.data = None

        self._get_recipes()

    def _get_recipes(self):
        if not self.data or self.refresh_time < datetime.datetime.utcnow():
            self.data = json.load(self.s3.Object(self.s3_bucket, self.s3_key).get().get('Body'))
            print('Refreshed data')
            self.refresh_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=CACHE_TTL)

        return self.data

    def all(self):
        return self._get_recipes()

    def single(self, title):
        recipes = self._get_recipes()
        if title in recipes:
            return recipes[title]

        return False

recipes = Recipes(
    os.environ.get('S3_BUCKET', 'not-your-grandmas-recipe-box'),
    os.environ.get('S3_KEY', 'recipe-box-conversion.json')
)
