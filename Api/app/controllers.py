"""This module will serve the api request."""
import os, ast, imp, json, datetime
from bson.json_util import dumps
from config import client
from app import app
from flask import request, jsonify
from datetime import date
from werkzeug.utils import secure_filename


# Allowed files extensions
ALLOWED_EXTENSIONS = set(["mov"])

# Folder locations for uploads
SUSPECTS_UPLOAD_FOLDER = "/assets/suspects/"
VIDEOS_UPLOAD_FOLDER = "/assets/videos/"

# Import the helpers module
helper_module = imp.load_source('*', './app/helpers.py')

# Select the database
db = client['api']
# Select the collection
usersCol = db['users']
suspectsCol = db['suspects']

@app.route('/', methods=['GET'])
def mainPage():
    return jsonify({"message": "I'm alive."})

@app.route('/videos', methods=['GET'])
def getVideos():
    ar = usersCol.find({})
    return dumps(ar)

@app.route('/videos', methods=['POST'])
def postVideos():
    try:
        query_params = helper_module.parse_query_params(request.query_string)

        if (query_params != None and
            'title' in query_params and
            'userid' in query_params and
            'filename' in query_params):

            storedUser = usersCol.find_one({"userid": query_params['userid']})
            
            newVideo = {
                "title": query_params["filename"],
                "local": str(os.path.join(VIDEOS_UPLOAD_FOLDER, query_params['filename'])),
                "timestamp": datetime.datetime.utcnow()
            }

            if(storedUser != None):
                result = usersCol.update({"_id": storedUser['_id']},
                    {"$push": {"videos": newVideo}},
                    upsert=True)
                
            else:
                result = usersCol.insert_one({"userid": query_params['userid'], "videos": newVideo})

            return result, 200
        else:
            return "Missing Parameter", 400
    except Exception as e:
        print(e)
        return "Server Error", 500

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

        if (query_params != None and
            'filename' in query_params and
            'file' in request.files):

            file = request.files['file']
            if(file.filename == ''):
                return "Missing Parameter", 400

            storedSuspect = suspectsCol.find_one({})
            newSuspect = {
                "title": query_params["filename"],
                "local": str(os.path.join(SUSPECTS_UPLOAD_FOLDER, query_params['filename'])),
                "timestamp": datetime.datetime.utcnow()
            }

            if(storedSuspect != None):
                result = suspectsCol.update({"_id": storedSuspect['_id']},
                    {"$push": {"suspects": newSuspect}},
                    upsert=True)
            else:
                result = suspectsCol.insert({"suspects": newSuspect})
            
            return result, 200
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
