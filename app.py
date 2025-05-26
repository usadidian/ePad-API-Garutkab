import ast
import decimal
import mimetypes
import os

from dotenv import load_dotenv
from flasgger import Swagger

load_dotenv()
import cloudinary
from flask import Flask, render_template
from flask_cors import CORS

from config.config import cloudinary_api_secret, cloudinary_cloud_name, cloudinary_api_key
from config.database import *
from router_api import *
from flask.json import JSONEncoder
from datetime import date
from flask import request

cloudinary.config(
    cloud_name=cloudinary_cloud_name,
    api_key=cloudinary_api_key,
    api_secret=cloudinary_api_secret
)

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, date):
                # return obj.isoformat()
                return obj.strftime("%Y-%m-%d %H:%M:%S.%f")
            if isinstance(obj, decimal.Decimal):
                return str(obj)
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)


app = Flask(__name__, template_folder="templates")
swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "ePad API Garutkab",
        "description": "ePad API specification for Garutkab",
        "version": "1.0.0"
    },
    "tags": [
        {
            "name": "Authentication",
            "description": "User Login"
        },
        {
            "name": "Revenue Summary",
            "description": "Revenue summary reporting"
        },
        {
            "name": "Revenue Categories",
            "description": "Revenue category listing"
        },
        {
            "name": "Tax Entities",
            "description": "Registered taxpayer entities"
        },
        {
            "name": "Revenue Log Type",
            "description": "Log of revenue transactions or actions"
        },
        {
            "name": "Transactions",
            "description": "Tax payment transaction records"
        }
    ],

    "securityDefinitions": {
        "ApiKeyAuth": {
            "type": "apiKey",
            "name": "APIKey",
            "in": "header"
        }
    },
    "security": [  # ⬅️ tambahkan ini
        {
            "ApiKeyAuth": []
        }
    ]
}

swagger = Swagger(app, template=swagger_template)
CORS(app, resources={r"/*": {"origins": "http://localhost:4200"}}, supports_credentials=True)



app.json_encoder = CustomJSONEncoder


connection_map = ast.literal_eval(os.environ.get('EPAD_DB_CONNECTIONS'))
app.config['SQLALCHEMY_DATABASE_URI'] = connection_map['default']
app.config['SQLALCHEMY_BINDS'] = connection_map
# app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

cors = CORS(app, origins="*", supports_credentials=True)

db.init_app(app)
api.init_app(app)

mimetypes.add_type('application/javascript', '.mjs')


@app.before_request
def before_request():
    origin = request.headers.get('Origin')
    # print(f'ORIGIN: {origin}')
    if origin:
        origin = origin.replace('http://', '').replace('https://', '').replace('/', '')
        print(f'ORIGIN: {origin}')
        if origin in connection_map.keys():
            # print('FALSE')
            db.choose_tenant(origin)
        else:
            db.choose_tenant('default')
    else:
        db.choose_tenant('default')


@app.teardown_request
def teardown_request(exception):
    if exception:
        db.session.rollback()
    db.session.remove()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/static/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    if os.environ.get('EPAD_BASE_URL_PORT'):
        app.run(host=os.environ.get('EPAD_BASE_URL'), port=os.environ.get('EPAD_BASE_URL_PORT'))
    else:
        app.run(host=os.environ.get('EPAD_BASE_URL'), port=8080)

