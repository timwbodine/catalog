from models import Base, Recipe, Ingredient, Cuisine, User
from flask import Flask, jsonify, request
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
import sys
import codecs

engine=create_engine('sqlite:///recipes.db')

Session = sessionmaker(bind=engine)
session = Session()
testUser = User(name='Testy Testerson', password_hash = 'kjdflkjsdlfkjasdf')
session.add(testUser)
pizza = Cuisine(cuisine_id="Pizza")
chinese = Cuisine(cuisine_id="Chinese")
mexican = Cuisine(cuisine_id="Mexican")
sushi = Cuisine(cuisine_id="Sushi")
session.add_all([pizza, chinese, mexican, sushi])
session.commit()
pizzaRecipe = Recipe(name="yummy pizza pie", description="it's molto bene!", difficulty="0", cuisine_id=pizza.cuisine_id, user_id=testUser.id)
chineseRecipe = Recipe(name="funky fried rice", description="it's funky!", difficulty="2", cuisine_id=chinese.cuisine_id, user_id=testUser.id)
mexicanRecipe = Recipe(name="grody gordita", description="it's totes grody", difficulty="3", cuisine_id=mexican.cuisine_id, user_id=testUser.id)
sushiRecipe = Recipe(name="californication roll", description="mixes food with bodily fluids", difficulty="1", cuisine_id=sushi.cuisine_id, user_id = testUser.id)
session.add(pizzaRecipe)
session.add(mexicanRecipe)
session.add(chineseRecipe)
session.add(sushiRecipe)
session.commit()
result = session.query(Recipe).all()
print result

