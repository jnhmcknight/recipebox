
from urlparse import urlparse
from flask import Flask, render_template, redirect, url_for, request

from application.cache import recipes

app = Flask(__name__)

@app.template_filter('hostname_link')
def hostname(url):
    if not url:
        return 'Unknown'

    parsed = urlparse(url)
    if not parsed.hostname:
        return url

    return '<a href="{}" target="_blank">{}</a>'.format(url, parsed.hostname)


@app.template_filter('sorted')
def mysorted(mylist):
    return sorted(mylist)


@app.template_filter('nl2br')
def nl2br(string):
    return string.replace('\n', '<br/>')


@app.route("/")
def index():
    title = 'All Recipes'
    return render_template('recipes.html', recipes=recipes.all(), title=title.decode('utf-8'))


@app.route("/recipe/<string:id>")
def recipe(id):
    single = recipes.single(id)
    return render_template('recipe.html', recipe=single)


@app.route("/cat")
def categories():
    return render_template('categories.html', categories=recipes.categories())


@app.route("/cat/<string:id>")
def category(id):
    subset = {}
    for recipe in recipes.in_category(id):
        subset.update({recipe: recipes.single(recipe)})
    title = 'Recipes classified as {}'.format(id)
    return render_template('recipes.html', recipes=subset, title=title.decode('utf-8'))


@app.route("/search", methods=['GET'])
def search():
    return render_template('search.html')

@app.route("/search", methods=['POST'])
def perform_search():
    if not request.values.get('term'):
        return redirect(url_for('search'))

    term = request.values.get('term').encode('utf-8').lower()

    recipelist = {}
    search_type = request.values.get('type', 'ingredient')

    allrecipes = recipes.all()
    for recipe in allrecipes.keys():
        if search_type == 'ingredient':
            for ingredient in allrecipes[recipe].get('ingredients').split('\n'):
                if term in ingredient.encode('utf-8').lower():
                    recipelist.update({recipe: allrecipes[recipe]})
                    break

        elif search_type == 'instruction':
            for instruction in allrecipes[recipe].get('instructions').split('\n'):
                if term in instruction.encode('utf-8').lower():
                    recipelist.update({recipe: allrecipes[recipe]})
                    break

        elif term in recipe.encode('utf-8').lower():
            recipelist.update({recipe: allrecipes[recipe]})

    title = 'Found {} Recipes for "{}" in {}s'.format(len(recipelist.keys()), term, search_type)
    return render_template('recipes.html', recipes=recipelist, title=title.decode('utf-8'))
