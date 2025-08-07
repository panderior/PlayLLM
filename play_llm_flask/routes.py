import io
import base64
from flask import Flask, request, render_template, jsonify, Response, json, jsonify, abort
from sqlalchemy import func, desc
from play_llm_flask import app
# from play_llm_flask.models import 
# from play_llm_flask.tasks import 


@app.route('/')
def home():
    return "Hello, Flask!"