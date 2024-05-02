from flask import Flask, request, render_template, Blueprint
from werkzeug.utils import secure_filename
import sqlite3
import os
import database

database_routes = Blueprint("database_routes", __name__)

@database_routes.route('/reset_database', methods=['GET', 'POST'])
def reset_database():
    if request.method == 'POST':
        password = request.form.get('password')
        correct_password = os.environ.get('ADMIN_PASSWORD', 'password')
        if password == correct_password:
            database.reset_tables()
            return "Database reset successfully."
        else:
            return "Incorrect password."
    return render_template('reset_database.html')

@database_routes.route('/upload_teams', methods=['GET', 'POST'])
def upload_teams():
    if request.method == 'POST':
        password = request.form.get('password')
        correct_password = os.environ.get('ADMIN_PASSWORD', 'password')
        if password == correct_password:
            file = request.files['file']
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join('uploads', "teams.csv"))
                # Process the file and add the teams to the database
                # You'll need to implement this function
                database.read_teams(os.path.join('uploads', 'teams.csv'))
                return "Teams uploaded successfully."
            else:
                return "No file selected."
        else:
            return "Incorrect password."
    return render_template('upload_teams.html')

@database_routes.route('/upload_tiles', methods=['GET', 'POST'])
def upload_tiles():
    if request.method == 'POST':
        password = request.form.get('password')
        correct_password = os.environ.get('ADMIN_PASSWORD', 'password')
        if password == correct_password:
            file = request.files['file']
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join('uploads', "tiles.csv"))
                # Process the file and add the tiles to the database
                # You'll need to implement this function
                database.read_tiles(os.path.join('uploads', 'tiles.csv'))
                return "Tiles uploaded successfully."
            else:
                return "No file selected."
        else:
            return "Incorrect password."
    return render_template('upload_tiles.html')