from flask import Flask


def create_app():
    server = Flask(__name__)
    return server