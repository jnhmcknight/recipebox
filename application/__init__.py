
from urlparse import urlparse
from flask import Flask, render_template

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
    return render_template('recipes.html', recipes=recipes.all())


@app.route("/recipe/<string:id>")
def recipe(id):
    single = recipes.single(id)
    print(single)
    return render_template('recipe.html', recipe=single)


@app.route("/cat")
def categories():
    return render_template('categories.html', categories=recipes.categories())


@app.route("/cat/<string:id>")
def category(id):
    subset = {}
    for recipe in recipes.in_category(id):
        subset.update({recipe: recipes.single(recipe)})
    return render_template('recipes.html', recipes=subset)


@app.route("/search")
def search():
    pass
