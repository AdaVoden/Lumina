from flask import Flask, render_template, jsonify, request, abort
from database import Database

app = Flask(__name__, template_folder="templates", static_folder="static")


@app.route("/")
def dashboard():
    with Database() as db:
        stats = db.get_last_snapshot()
        return render_template("dashboard.html",
                                followers = stats["total_followers"],
                                active = stats["active_count"],
                                never_posted = stats["never_posted_count"],
                                disabled = stats["disabled_count"],
                                handle = stats["account_handle"],
                                last_updated = stats["timestamp"])


@app.route("/snapshots")
def snapshots():
    pass