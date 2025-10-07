from flask import Flask, render_template, jsonify, request, abort
from database import Database

app = Flask(__name__, template_folder="templates", static_folder="static")
db = Database()

@app.route("/")
def dashboard():
    pass

@app.route("/snapshots")
def snapshots():
    pass