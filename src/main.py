"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Todo
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route("/todos", methods=["GET"])
def get_todos():

    all_todos = Todo.query.all()
    todos_serializado = list(map(lambda n: n.serialize(), all_todos))
    return jsonify(todos_serializado), 200

@app.route("/todos", methods=["POST"])
def post_todos():

    body = request.get_json()
    print(body["label"])

    label = Todo(label=body["label"], done=body["done"])
    db.session.add(label)
    db.session.commit()

    resp ={ 
        "msg": "Tarea añadida"
    }

    return jsonify(resp), 200

@app.route("/todos/<int:position>", methods=["DELETE"])
def delete_todos(position):

    print(position)
    tarea = Todo.query.get(position)
    if tarea is None:
        raise APIException('User not found', status_code=404)
    db.session.delete(tarea)
    db.session.commit()

    resp ={
        "msg":"Tarea eliminada"
    }

    return jsonify(resp), 200
# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
