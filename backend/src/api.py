import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
'''
@app.route('/drinks')
def get_drinks():
    try:
        # Query to get all drinks from database
        drinks = Drink.query.all()

        return jsonify({
            'success': True,
            'drinks': [drink.short() for drink in drinks] # Formatting them according to the short method from models
        }), 200
    except:
        abort(404)

'''
@TODO implement endpoint
    GET /drinks-detail
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drink_detail(jwt):
    try:
        # Query to get all drinks from database
        drinks = Drink.query.all()

        return jsonify({
            'success': True,
            'drinks': [drink.long() for drink in drinks] # Formatting them according to the long method from models
        }), 200
    except:
        abort(404)

'''
@TODO implement endpoint
    POST /drinks
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(jwt):
    body = request.get_json()

    if not ('title' in body and 'recipe' in body): # If statement to ensure there is a title and recipe from the json form
        abort(422)

    title = body.get('title', None)
    recipe = body.get('recipe', None)
        
    try:
        drink = Drink(title =title, recipe = json.dumps(recipe))
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': drink.long()
        }), 200

    except:
        abort(422)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
'''
@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(jwt, id):
    drink = Drink.query.get(id) # Query to get drinks record for that specific ID

    if drink is None:
        abort(404)

    try:
        body = request.get_json()

        title = body.get('title')
        recipe = body.get('recipe')

        if title:
            drink.title = title
        if recipe: 
            drink.recipe = recipe

        # Updating the drinks information according to that provided by the user
        drink.update()

        return jsonify({
            'success': True,
            'drinks': drink.long()
        })
    except:
        abort(422)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
'''
@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, id):

    # Query to get specific drink record via id
    drink = Drink.query.get(id)

    if drink is None:
        abort(404)

    try:
        # Deleting the specific drinks record from the database
        drink.delete()
        
        return jsonify({
            'success': True,
            'delete': id
        })
    except:
        abort(422)

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def handle_auth_error(exception):
    return jsonify({
        'success': False,
        'error': exception.status_code,
        'message': exception.error
    }), 401