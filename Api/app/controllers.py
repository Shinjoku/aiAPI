"""This module will serve the api request."""
from bson.json_util import dumps
from config import client
from app import app
from flask import request, jsonify
from datetime import date
import json
import ast
import imp
import os
from werkzeug.utils import secure_filename

# Import the helpers module
helper_module = imp.load_source('*', './app/helpers.py')

# Select the database
db = client['api']
# Select the collection
usersCol = db['users']
suspectsCol = db['suspects']

# Allowed files extensions
extensions = set(["mov"])

@app.route("/", methods=['GET'])
def default_route():
    """
       Function to fetch the pads.
    """
    try:
        # Call the function to get the query params
        query_params = helper_module.parse_query_params(request.query_string)
        # Check if dictionary is not empty
        if query_params:
            return jsonify(query_params)
        else:
            return str("AH BININO")
    except:
        # Error while trying to fetch the resource
        # Add message for debugging purpose
        return "", 500

@app.route('/videos', methods=['GET'])
def getVideos():
    ar = usersCol.find({})
    return dumps(ar)

# @app.route('/videos', methods=['POST'])
# def postVideos():
#     pass

@app.route('/results', methods=['GET'])
def getResults():
    try:
        query_params = helper_module.parse_query_params(request.query_string)
        if (query_params != ""):
            result = userCol.find({userId: srt(query_params)})
            return jsonify(result)
        else:
            return "Missing Parameter", 400
    except:
        return "Server Error", 500

@app.route('/suspects', methods=['POST'])
def postSuspects():
    try:
        query_params = helper_module.parse_query_params(request.query_string)
        if (query_params != ""):
            storedSuspect = suspectsCol.find_one({})
            newSuspect = {
                "title": "MUDOU O FILHO DA PUTA",
                "local": "/bataat",
                "timestamp": ""
            }

            result = suspectsCol.update({'_id': storedSuspect['_id']},
                {'$push': {'suspects': newSuspect}},
                upsert=True)
            return result.raw_result, 200
        else:
            return "Missing Parameter", 400
    except Exception as e:
        print(e)
        return "Server Error", 500

@app.errorhandler(404)
def page_not_found(e):
    """Send message to the user with notFound 404 status."""
    # Message to the user
    message = {
        "err":
            {
                "msg": "This route is currently not supported."
            }
    }
    # Making the message looks good
    resp = jsonify(message)
    # Sending OK response
    resp.status_code = 404
    # Returning the object
    return resp
