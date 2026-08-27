from flask import Flask
from config import Config
from app import db


def create_app():
    app = Flask(__name__)
    return app
