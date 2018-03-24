from models import Base, Cuisine, Recipe, User, Consumable, Ingredient
from flask import Flask, jsonify, request
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
import sys
import codecs

sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

engine = create_engine('sqlite:///recipes.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

@app.route('/allrecipes/json', methods = ['GET', 'POST'])
def all_recipes_handler():
    if request.method == 'GET':
        recipes = session.query(Recipe).all()
        print recipes
        return jsonify(recipes = [i.serialize for i in recipes])
    if request.method == 'POST':
        name = request.args['name']
        description = request.args['description']
        difficulty = request.args['difficulty']
        cuisine_id = request.args['cuisine_id']
        user_id = request.args['user_id']

@app.route('/cuisines/json', methods = ['GET'])
def all_cuisines_handler():
    if request.method == 'GET':
        cuisines = session.query(Cuisine).all()
        print cuisines
        return jsonify(cuisines = [i.serialize for i in cuisines])

@app.route('/cuisines/<string:cuisine_id>/recipes/json', methods = ['GET'])
def cuisine_recipes_handler(cuisine_id):
    if request.method == 'GET':
        recipes = session.query(Recipe).filter_by(cuisine_id=cuisine_id).all()
        return jsonify(recipes =[i.serialize for i in recipes])

@app.route('/cuisines/<string:cuisine_id>/recipes/<int:id>/json', methods = ['GET','PUT','DELETE'])
def recipe_handler(id, cuisine_id):
    if request.method == 'GET':
        recipe = session.query(Recipe).filter_by(id=id, cuisine_id=cuisine_id).one()
        return jsonify(RecipeAttributes = recipe.serialize)
    if request.method == 'PUT':
        name = request.args['name']
        description = request.args['description']
        difficulty = request.args['difficulty']
        cuisine_id = request.args['cuisine_id']
    if request.method == 'DELETE': 
        recipe = session.query(Recipe).filter_by(id=id).one()
        session.delete(recipe)
        session.commit()
        return "Recipe Deleted."

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
