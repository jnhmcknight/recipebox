
# Lambda RecipeBox

This is a _very_ simplistic recipe box, using a JSON file of recipes and categories. It is designed to run under AWS Lambda, but as it uses Flask, can just as easily be run standalone. It was created to view recipes that had been exported from a very wonderful iOS app, [The Recipe Box](https://itunes.apple.com/us/app/the-recipe-box-your-kitchen-your-recipes/id414537274?mt=8), which doesn't have a desktop version to sync to.

So, when your iOS device has no more charge, what are you to do? You plug it in, send yourself an export of all the recipes, and setup this little web viewer. Boom. You can now review your recipes on any web connected device. There are no editing features builtin, so anything you want to edit, you'll need to do so in the Recipe Box app and re-export the recipes.

In the `unarchiving` folder, there is a special program to convert your recipe box export into a usable JSON data file. The instructions for doing so are there. To export your collection, go to the main recipes list and send all your recipes to an email address that you have access to. The conversion program must be run on Mac OS with XCode installed as it uses proprietary Apple libs.
