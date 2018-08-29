"""
Convert a recipe box shared plist file to usable json

This is a heavily modified version of https://github.com/whyallyn/unarchive-plist

"""

import argparse
import base64
import boto3
import botocore
import hashlib
import json
import os
import sys
import unidecode

# pylint: disable=wildcard-import
# pylint: disable=unused-wildcard-import
from Foundation import *
from PyObjCTools.Conversion import pythonCollectionFromPropertyList
import objc

translated = {
    'creationDate': 'creation_date',
    'handsOnTime': 'hands_on_time',
    'ingredientsListing': 'ingredients',
    'instructions': 'instructions',
    'ovenTemporature': 'temperature',
    'rating': 'rating',
    'sourceAsString': 'source',
    'title': 'title',
    'totalTime': 'total_time'
}

def nskeyedarchive_to_json(plist_name, s3_bucket=None):
    """Convert a NSKeyedArchive to a JSON data file."""

    s3 = None
    if s3_bucket:
        s3 = boto3.resource('s3')

    try:
        # unarchive plist into a nsdict
        nsdict = NSKeyedUnarchiver.unarchiveObjectWithFile_(plist_name)
    except objc.error as err:
        print("[ERROR] %s" % err)
        sys.exit(1)

    recipes = {}
    categories = {}
    if nsdict:

        for item in nsdict["setOfRecipes"]:
            recipe_hash = hashlib.sha1(item.encode('utf-8')).hexdigest()
            recipe_id = unidecode.unidecode(item).lower()
            data = nsdict["setOfRecipes"][item]
            attributes = {}
            for attr in data['attributeDictionary']:
                if attr not in translated:
                    continue

                value = unicode(data['attributeDictionary'][attr]).strip()
                if attr == 'title':
                    value = value.title()

                attributes.update({translated[attr]: value})

            key = 'browseThumbnail'
            if key in data and data[key]:
                try:
                    body = base64.b64encode(pythonCollectionFromPropertyList(data[key]['imageData']))
                    s3.Object(s3_bucket, 'images/{}'.format(recipe_hash)).put(
                        Body=base64.b64decode(body),
                        ACL='public-read')
                    print('Uploaded image for: {}'.format(recipe_id))
                except botocore.exceptions.NoCredentialsError:
                    pass

                if s3_bucket:
                    attributes.update({'image': 'https://{}.s3.amazonaws.com/images/{}'.format(s3_bucket, recipe_hash)})

            key = 'categories'
            if key in data and data[key]:
                cats = set()
                for category in data[key]:
                    name = category['RBCategoryObjectName']
                    if name not in categories:
                        categories.update({name: []})
                    cats.add(name)
                    categories[name].append(recipe_id)

                attributes.update({'categories': list(cats)})

            recipes.update({recipe_id: attributes})
    else:
        print("[ERROR] Failed to unarchive %s. Check input name." % plist_name)
        sys.exit(1)

    return {'recipes': recipes, 'categories': categories}


def parse_arguments():
    """Argument Parser."""
    parser = argparse.ArgumentParser(
        description=__doc__)
    parser.add_argument(
        "-r",
        "--read",
        dest="plist_in",
        required=True,
        help="rbox file exported from The Recipe Box (iOS app).")
    parser.add_argument(
        "-w",
        "--write",
        dest="plist_out",
        help="Filename to write the JSON data.")
    parser.add_argument(
        "-s",
        "--s3",
        dest="s3_bucket",
        default=None,
        help="S3 Bucket to upload image files.")
    return parser.parse_args()


def main():
    """Main function."""
    args = parse_arguments()
    recipes = nskeyedarchive_to_json(args.plist_in, args.s3_bucket)
    if not args.plist_out:
        print(json.dumps(recipes, indent=4))
    else:
        with open(args.plist_out, 'w') as outfile:
            outfile.write(json.dumps(recipes, indent=4))


if __name__ == "__main__":
    sys.exit(main())

