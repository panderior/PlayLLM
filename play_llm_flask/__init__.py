from flask import Flask
from concurrent.futures import ThreadPoolExecutor
import logging
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from celery import Celery
import os

# Load environment variables for database
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PWD = os.getenv('DB_PWD')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = int(os.getenv('DB_PORT'))

# Load environment variables for Celery Redis
CELERY_REDIS_IP = os.getenv('CELERY_REDIS_IP')
CELERY_REDIS_PORT = int(os.getenv('CELERY_REDIS_PORT'))
CELERY_BROKER_URL = f'redis://{CELERY_REDIS_IP}:{CELERY_REDIS_PORT}/0'
CELERY_RESULTS_URL = f'redis://{CELERY_REDIS_IP}:{CELERY_REDIS_PORT}/0'

# Load enviroment varibales for ollama server
OLLAMA_SERVER_IP = os.getenv('OLLAMA_SERVER_IP')
OLLAMA_SERVER_PORT = int(os.getenv('OLLAMA_SERVER_PORT'))

def db_init_app(app: Flask):
    """
    A helper function to create a DB connection with SQL Alchemy
    """
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        'mysql+pymysql://'
        f'{DB_USER}:{DB_PWD}'
        f'@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    )
    # Disable modification tracking to save memory:
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = SQLAlchemy(app)
    
    return db

# setup Flask app and mouldes
app = Flask(__name__)
db = db_init_app(app)
bcrypt = Bcrypt()

# setup logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

executor = ThreadPoolExecutor(max_workers=5)

from play_llm_flask import routes

# create tables if they don't exist

# from play_llm_flask.models import 
# with app.app_context():
#     db.create_all()
#     logger.info("Database tables checked/created.")