from models import Base, Cuisine, Recipe, User, Ingredient
from flask import Flask, jsonify, request, redirect, url_for
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from flask import session as login_session
from flask import render_template
import random, string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from google.oauth2 import id_token
from google.auth.transport import requests as googleRequests
import sys
import codecs
import httplib2
import json
from flask import make_response
import requests
from xml.etree import ElementTree
# use PoolListener to enforce foreign key constrainst in sqlite
from sqlalchemy.interfaces import PoolListener
class ForeignKeysListener(PoolListener):
    def connect(self, dbapi_con, con_record):
        db_cursor = dbapi_con.execute('pragma foreign_keys=ON')

sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)
CLIENT_ID = json.loads(open ('client_secrets.json','r').read())['web']['client_id']
engine = create_engine('sqlite:///recipes.db', listeners=[ForeignKeysListener()])
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)


@app.route('/googledisconnect')
def googleDisconnect():
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/googletokenconnect', methods = ['POST'])
def googleTokenConnect():
    CLIENT_ID  = '958193736755-h6gvechgf31qm5eedvkisqectdkp5i0u.apps.googleusercontent.com'
    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        print request.headers
        token = request.form['idtoken']
        print token
        print requests.Request()
        idinfo = id_token.verify_oauth2_token(token, googleRequests.Request(), CLIENT_ID)
        print(idinfo)
        # Or, if multiple clients access the backend server:
        # idinfo = id_token.verify_oauth2_token(token, requests.Request())
        # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
        #     raise ValueError('Could not verify audience.')

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        # If auth request is from a G Suite domain:
        # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
        #     raise ValueError('Wrong hosted domain.')

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        gplus_id = idinfo['sub']
        stored_gplus_id = login_session.get('gplus_id')
        if login_session.get('access_token') is not None and gplus_id == stored_gplus_id:
            response = make_response(json.dumps('Current user is already connected; updating access token.'),200)
            response.headers['Content-Type'] = 'application/json'
            login_session['access_token'] = token 
            return response
        login_session['access_token'] = token
        login_session['gplus_id'] = gplus_id
        user_id = getUserId(idinfo['email'])

        if user_id is not None:
            user = getUserInfo(user_id)
            print("fetching user data from database...")
            login_session['username'] = user.name
            login_session['email'] = user.email
            login_session['picture'] = user.picture
            login_session['id'] = user.id
        else:
            login_session['username'] = idinfo['name']
            login_session['picture'] = idinfo['picture']
            login_session['email'] = idinfo['email']
            login_session['id'] = create_user['login_session']
        
        output = ''
        output += '<h1>Welcome, '
        output += login_session['username']
        output += '!</h1>'
        output += '<img src="'
        print("TYPES %s %s") %(str(login_session['picture']), login_session['username'])
        output += login_session['picture']
        output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
        print("you are now logged in as %s" % login_session['username'])
        print "done!"
        return output
    except ValueError:
        # Invalid token
        pass
@app.route('/login') 
def showLogin():
    state=''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    print(state)
    return render_template('newLogin.html', STATE=state)
    return "The current session state is %s" %login_session['state']
    
@app.route('/createrecipe', methods = ['GET', 'POST'])
def createRecipe():
    if request.method == 'GET':
        if 'username' not in login_session:
            return redirect(url_for('showLogin'))
        return render_template('newrecipe.html')
    if request.method == 'POST':
        print(login_session['username']) 
        print(login_session['email'])
        print("that is the current username")
        newRecipe = Recipe(name = request.form['name'], description = request.form['description'], difficulty = request.form['difficulty'], cuisine_id = request.form['cuisine'], user_id = getUserId(login_session['email']))
        session.add(newRecipe)
        session.commit()
        return redirect(url_for('create_ingredient', cuisine_id=newRecipe.cuisine_id, recipe_id=newRecipe.id))
@app.route('/allrecipes', methods = ['GET', 'POST'])
def all_recipes_handler():
    if request.method == 'GET':
        recipes = session.query(Recipe).all()
        cuisines = session.query(Cuisine).all()
        print recipes
        if 'username' not in login_session:
            user_id = None
        else:
            user_id = getUserId(login_session['email'])
        return render_template('allrecipes.html', recipes=recipes, cuisines=cuisines, user_id=user_id)
        return jsonify(recipes = [i.serialize for i in recipes])

    if request.method == 'POST':
        if 'username' not in login_session:
            return redirect(url_for('showLogin'))
        name = request.args['name']
        description = request.args['description']
        difficulty = request.args['difficulty']
        cuisine_id = request.args['cuisine_id']
        newRecipe = Recipe(name=name, description=description, difficulty=difficulty, cuisine_id = cuisine_id,user_id=login_session['user_id'])
        session.add(newRecipe)
        session.commit()
@app.route('/cuisines', methods = ['GET'])
def all_cuisines_handler():
    if request.method == 'GET':
        cuisines = session.query(Cuisine).all()
        print cuisines
        return render_template('showcuisines.html', cuisines=cuisines)
        return jsonify(cuisines = [i.serialize for i in cuisines])

@app.route('/cuisines/<string:cuisine_id>/recipes/', methods = ['GET'])

def cuisine_recipes_handler(cuisine_id):
    if request.method == 'GET':
        if 'username' not in login_session:
            user_id = None
        else:
            user_id = getUserId(login_session['email'])
        recipes = session.query(Recipe).filter_by(cuisine_id=cuisine_id).all()
        return render_template("cuisinerecipes.html", recipes=recipes,cuisine=cuisine_id, user_id=user_id)
        return jsonify(recipes =[i.serialize for i in recipes])

@app.route('/cuisines/<string:cuisine_id>/recipes/<int:id>', methods = ['GET','PUT','DELETE'])
def recipe_handler(id, cuisine_id):
    recipe = session.query(Recipe).filter_by(id=id, cuisine_id=cuisine_id).one()
    ingredients = session.query(Ingredient).filter_by(recipe_id=id).all()
    creator=getUserInfo(recipe.user_id)
    if request.method == 'GET':
        if 'username' not in login_session or creator.id != login_session['id']:
            return render_template("recipe.html", cuisine_id=cuisine_id, user_id=None, recipe=recipe, ingredients=ingredients) 
        else:
            user_id = getUserId(login_session['email'])
        return render_template("recipe.html", cuisine_id=cuisine_id, user_id=user_id, recipe=recipe, ingredients=ingredients) 
        return jsonify(RecipeAttributes = recipe.serialize)
    if request.method == 'PUT':
        print("hello!")
        if 'username' not in login_session or creator.id != login_session['id']:
            return redirect(url_for("showLogin"))
        print(request.form['name'])
        print(recipe.name + recipe.description + recipe.difficulty + recipe.cuisine_id)
        print(session.query(Recipe).filter_by(id=id, cuisine_id=cuisine_id).one())
        recipe.name = request.form['name']
        recipe.description = request.form['description']
        recipe.difficulty = request.form['difficulty']
        recipe.cuisine_id = request.form['cuisine_id']
        print("still here")
        session.commit()
        return '200'

    if request.method == 'DELETE': 
        if 'username' not in login_session or creator.id != login_session['id']:
            return redirect(url_for("showLogin"))
        for ingredient in ingredients:
            session.delete(ingredient)
        session.delete(recipe)
        session.commit()
        return "Recipe Deleted."
@app.route('/cuisines/<string:cuisine_id>/recipes/<int:recipe_id>/newIngredient', methods =['GET','POST'])
def create_ingredient(cuisine_id, recipe_id):
    recipe = session.query(Recipe).filter_by(id=recipe_id).one()
    print(recipe.user_id)
    creator=getUserInfo(recipe.user_id)
    if 'username' not in login_session or creator.id != login_session['id']:
        return redirect(url_for("showLogin"))
    if request.method == 'GET':
        return render_template('createIngredient.html', recipe_id=recipe_id, cuisine_id=cuisine_id)
    if request.method == 'POST':
        ingredient = Ingredient(recipe_id = recipe_id, user_id = getUserId(login_session['email']), name = request.form['name'], amount = request.form['amount'], unit = request.form['unit'])
        session.add(ingredient)
        session.commit()
        return redirect(url_for('recipe_handler',cuisine_id=cuisine_id,id=recipe_id), 303)
@app.route('/cuisines/<string:cuisine_id>/recipes/<int:recipe_id>/ingredients/<int:id>', methods = ['GET', 'PUT', 'DELETE'])
def ingredient_handler(id, cuisine_id, recipe_id):
    ingredient = session.query(Ingredient).filter_by(id=id).one()
    cuisine_id=cuisine_id
    recipe_id=recipe_id
    creator=getUserInfo(ingredient.user_id)
    if 'username' not in login_session or creator.id != login_session['id']:
        return redirect(url_for("showLogin"))
    user_id = getUserId(login_session['email'])
    if request.method == 'GET':
        return render_template("editIngredient.html",user_id=user_id, recipe_id=recipe_id, cuisine_id=cuisine_id, ingredient=ingredient) 
    if request.method == 'PUT':
        editedIngredient =ingredient 
        editedIngredient.name = request.form['name']
        editedIngredient.amount = request.form['amount']
        editedIngredient.unit = request.form['unit']
        session.add(editedIngredient)
        session.commit()
        return(url_for('all_recipes_handler'))
    if request.method == 'DELETE':
        deletedIngredient = ingredient
        session.delete(deletedIngredient)
        session.commit()
        return(url_for('all_recipes_handler'))
def createUser(login_session):
    newUser = User(name = login_session['username'], email = login_session['email'], picture = login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email = login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

def getUserId(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None
    

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
