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

db_drop_and_create_all()

# ROUTES

@app.route('/drinks')
def get_drinks():
    """
    This function will return all drinks on the coffee in short format. 
    """

    drinks = Drink.query.all()

    # get the short description of drink
    drinks_short = [drink.short() for drink in drinks]

    result = {
        'success':True,
        'drinks': drinks_short
    }

    return jsonify(result), 200

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    """
    This function will return all drinks on the coffee with detail (long format). 
    """

    try:
        drinks = Drink.query.all()

        # get the long description of drink
        drinks_long = [drink.long() for drink in drinks]

        result = {
            'success':True,
            'drinks': drinks_long
        }

        return jsonify(result), 200

    except Exception as error:
        abort(403)

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(jwt):
    """
    This function will add a new drink in the coffee. 
    """
    # fetch request as json object
    data = request.get_json()

    title = data['title']
    recipe = data['recipe']

    if isinstance(recipe,dict):
        recipe = [recipe]

    new_drink = Drink(
        
        title = title,
        
        # casting recipe dictionary into json object
        recipe = json.dumps(recipe)
    )

    new_drink.insert()

    # get the long description of drink
    drink_long = [new_drink.long()]

    result = {
        'success': True,
        'drinks': drink_long
    }

    return jsonify(result), 200

@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(jwt, drink_id):
    """
    This function will update the drink details in the coffee. 
    """
    # fetch request as json object
    data = request.get_json()

    new_title = data.get('title', None)
    new_recipe = data.get('recipe', None)

    drink = Drink.query.filter(Drink.id == drink_id).first()

    if drink is None:
        abort(404)
    
    if new_title:
        drink.title = data['title']
    if new_recipe:
        drink.recipe = data['recipe']

    if new_title or new_recipe:
        drink.update()

    # get the long description of drink
    drink_long = [drink.long()]

    result = {
        'success': True,
        'drinks': drink_long
    }

    return jsonify(result), 200


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):
    """
    This function will delete a drink in the coffee. 
    """
    drink = Drink.query.filter(Drink.id == drink_id).first()

    if drink is None:
        abort(404)

    drink.delete()

    result = {
        'success': True,
        'delete': drink_id
    }

    return jsonify(result), 200


# Error Handling


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad Request'
    }), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': 'unauthorized'
    }), 401
    
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        'success': False,
        'error': error.status_code,
        'message': error.error['description']
    }), error.status_code