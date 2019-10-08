"""This module will serve the api request."""
import os, ast, imp, json, datetime
from bson.json_util import dumps
from config import client
from app import app
from flask import request, jsonify, send_file
from datetime import date
from werkzeug.utils import secure_filename

currentDir = os.getcwd()
MOCKED_RESULT = [
    {
        "name": "Eduardo",
        "milisec": "3841"
    },
    {
        "name": "Catarina",
        "milisec": "9374"
    },
    {
        "name": "Gabriela",
        "milisec": "15398"
    }
]

# Allowed files extensions
ALLOWED_EXTENSIONS = set(["mov", "jpg", "png"])

# Folder locations for uploads
SUSPECTS_UPLOAD_FOLDER = "assets/database/"
VIDEOS_UPLOAD_FOLDER = "assets/videos/"

# Import the helpers module
helper_module = imp.load_source('*', './Api/app/helpers.py')

# Select the database
db = client['api']
# Select the collection
usersCol = db['users']
suspectsCol = db['suspects']

@app.route('/', methods=['GET'])
def mainPage():
    return jsonify({"message": "I'm alive."})

@app.route('/videos', methods=['GET'])
def get_videos():
    try:
        query_params = helper_module.parse_query_params(request.query_string)
        if (query_params != None and 'userid' in query_params):
            userVideos = usersCol.distinct("results.local", {"userid": query_params['userid']})
            
            if (userVideos == None):
                result  = "User not found!"
            else:
                return send_file(userVideos, mimetype='video/quicktime')
            
            return jsonify(result), 200
        else:
            return "Missing Parameter", 400
    except Exception as e:
        print(e)
        return "Server Error", 500

@app.route('/videos', methods=['POST'])
def post_videos():
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
            saveFile = upload_file(request, "video")
            if (saveFile == "Success"):
                if(storedUser != None):
                    result = usersCol.update({"_id": storedUser['_id']},
                        {"$push": {"videos": newVideo}},
                        upsert=True)
                else:
                    videosArr = []
                    videosArr.append(newVideo)
                    result = usersCol.insert_one({"userid": query_params['userid'], "videos": videosArr})
            else:
                result = saveFile

            return str(result), 200
        else:
            return "Missing Parameter", 400
    except Exception as e:
        print(e)
        return "Server Error", 500

@app.route('/results', methods=['GET'])
def get_results():
    try:
        query_params = helper_module.parse_query_params(request.query_string)
        print(not query_params)
        if (not query_params):
            #
            #QUERY exemplo mongo
            #db.suspects.distinct("suspects.local", {_id: ObjectId("5d92a4bce5014c9226bcdc8e")})
            #
            #findResults = usersCol.distinct("results.local", {"userid": query_params['userid']})
            #if(findResults != None):
                #return send_file(findResults, mimetype='image/jpg')
            return jsonify(MOCKED_RESULT)
            # else:
            #     result = "Result not found!"

            return jsonify(result), 200
        else:
            return "Missing Parameter", 400
    except:
        return "Server Error", 500

@app.route('/suspects', methods=['GET'])
def get_suspects():
    try:
        findSuspects = suspectsCol.distinct("suspects.local")
        if (findSuspects == None):
            result =  "Suspects not found!"
        else:
            return send_file(findSuspects, mimetype='image/jpg')

        return jsonify(result), 200
    except Exception as e:
        print(e)
        return "Server Error", 500

@app.route('/suspects', methods=['POST'])
def post_suspects():
    try:
        query_params = helper_module.parse_query_params(request.query_string)
        print(request.files)
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

            saveFile = upload_file(request, "image")
            if (saveFile == "Sucess"):
                if(storedSuspect != None):
                    result = suspectsCol.update({"_id": storedSuspect['_id']},
                        {"$push": {"suspects": newSuspect}},
                        upsert=True)
                else:
                    suspectsArr = []
                    suspectsArr.append(newSuspect)
                    result = suspectsCol.insert({"suspects": suspectsArr})
            else: 
                result = saveFile
            
            return str(result), 200
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

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_file(request, type):
    try:
        if 'file' not in request.files:
            return ('no file part.')
        file = request.files['file']
        if file  and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if type == "video":
                uploadFolder = os.path.join(currentDir, VIDEOS_UPLOAD_FOLDER)
                try:
                    file.save(os.path.join(uploadFolder, filename))
                except:
                    os.mkdir(uploadFolder)
                    file.save(os.path.join(uploadFolder, filename))
            else:
                uploadFolder = os.path.join(currentDir, SUSPECTS_UPLOAD_FOLDER)
                try:
                    file.save(os.path.join(uploadFolder, filename))
                except:
                    os.mkdir(uploadFolder)
                    file.save(os.path.join(uploadFolder, filename))
            return 'Success'
        else:
            return 'Extension not allowed'
    except Exception as e:
        return e
        
