from models import Base, Recipe, Ingredient, Cuisine, User, Difficulty
from flask import Flask, jsonify, request
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
import sys
import codecs

engine=create_engine('sqlite:///recipes.db')

Session = sessionmaker(bind=engine)
session = Session()
testUser = User(name='Testy Testerson', email='test@test.test', picture='http://www.test.test')
session.add(testUser)
pizza = Cuisine(cuisine_id="Pizza")
chinese = Cuisine(cuisine_id="Chinese")
mexican = Cuisine(cuisine_id="Mexican")
sushi = Cuisine(cuisine_id="Sushi")
indian = Cuisine(cuisine_id="Indian")
italian = Cuisine(cuisine_id="Italian")
easy = Difficulty(difficulty_id="Easy")
intermediate = Difficulty(difficulty_id="Intermediate")
advanced = Difficulty(difficulty_id="Advanced")
session.add_all([pizza, chinese, mexican, sushi, indian, italian, easy, intermediate, advanced])
session.commit()
pizzaRecipe = Recipe(name="yummy pizza pie", description="it's molto bene! Just throw sauce and cheese on dough, heat it up and enjoy!", difficulty="Easy", cuisine_id=pizza.cuisine_id, user_id=testUser.id)
chineseRecipe = Recipe(name="funky fried rice", description="it's funky!", difficulty="Intermediate", cuisine_id=chinese.cuisine_id, user_id=testUser.id)
mexicanRecipe = Recipe(name="grody gordita", description="it's totes grody", difficulty="Intermediate", cuisine_id=mexican.cuisine_id, user_id=testUser.id)
sushiRecipe = Recipe(name="californication roll", description="mixes food with bodily fluids", difficulty="Advanced", cuisine_id=sushi.cuisine_id, user_id = testUser.id)
session.add(pizzaRecipe)
session.add(mexicanRecipe)
session.add(chineseRecipe)
session.add(sushiRecipe)
session.commit()
ingredient1 = Ingredient(name="Pasta Sauce", recipe_id=pizzaRecipe.id, amount=1, user_id=testUser.id,unit="cup")
ingredient2 = Ingredient(name="Cheese", recipe_id=pizzaRecipe.id, amount=1, user_id=testUser.id,unit="pound")
ingredient3 = Ingredient(name="Bread", recipe_id=pizzaRecipe.id, amount=1, user_id=testUser.id,unit="blob")
session.add(ingredient1, ingredient2, ingredient3)
session.commit()
result = session.query(Recipe).all()
print result

