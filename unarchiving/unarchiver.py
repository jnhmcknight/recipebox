"""Convert a recipe box shared plist file to usable json"""

import argparse
import base64
import boto3
import hashlib
import json
import sys

# pylint: disable=wildcard-import
# pylint: disable=unused-wildcard-import
from Foundation import *
from PyObjCTools.Conversion import pythonCollectionFromPropertyList
import objc

s3 = boto3.resource('s3')
S3_BUCKET = 'not-your-grandmas-recipe-box'

special = {
    'browseThumbnail': 'image'
}

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

def nskeyedarchive_to_nsdict(plist_name):
    """Convert a NSKeyedArchive to a serializable NSDictionary."""
    try:
        # unarchive plist into a nsdict
        nsdict = NSKeyedUnarchiver.unarchiveObjectWithFile_(plist_name)
    except objc.error as err:
        print("[ERROR] %s" % err)
        sys.exit(1)

    recipes = {}
    if nsdict:

        # read SFLListItem "items" in order and return as list of nsdicts
        #for item in sorted(nsdict["items"], key=lambda k: k.order()):
        #    items.append(sfllistitem_to_nsdict(item))
        for item in nsdict["setOfRecipes"]:
            data = nsdict["setOfRecipes"][item]
            attributes = {}
            for attr in data['attributeDictionary']:
                if attr not in translated:
                    continue
                attributes.update({
                    translated[attr]: unicode(data['attributeDictionary'][attr])
                })

            key = 'browseThumbnail'
            if key in data and data[key]:
                print('Uploading image for: {}'.format(item.encode('utf-8')))
                name = hashlib.sha1(item.encode('utf-8')).hexdigest()
                body = base64.b64encode(pythonCollectionFromPropertyList(data[key]['imageData']))
                s3.Object(S3_BUCKET, 'images/{}'.format(name)).put(
                    Body=base64.b64decode(body),
                    ACL='public-read')
                attributes.update({'image': 'https://{}.s3.amazonaws.com/images/{}'.format(S3_BUCKET, name)})

            recipes.update({item: attributes})
    else:
        print("[ERROR] Failed to unarchive %s. Check input name." % plist_name)
        sys.exit(1)

    return recipes


def parse_arguments():
    """Argument Parser."""
    parser = argparse.ArgumentParser(
        description=__doc__)
    parser.add_argument(
        "-r",
        "--read",
        dest="plist_in",
        required=True,
        help="Property List (plist or sfl) file to convert.")
    parser.add_argument(
        "-w",
        "--write",
        dest="plist_out",
        help="Filename to write the new serialized plist.")
    return parser.parse_args()


def main():
    """Main function."""
    args = parse_arguments()
    recipes = nskeyedarchive_to_nsdict(args.plist_in)
    if not args.plist_out:
        print(json.dumps(recipes, indent=4))
    else:
        with open(args.plist_out, 'w') as outfile:
            outfile.write(json.dumps(recipes, indent=4))


if __name__ == "__main__":
    sys.exit(main())

