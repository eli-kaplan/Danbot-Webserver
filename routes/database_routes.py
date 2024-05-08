from flask import Flask, request, render_template, Blueprint, flash, redirect, send_from_directory
from werkzeug.utils import secure_filename
import sqlite3
import os
import database
from utils import autocomplete

database_routes = Blueprint("database_routes", __name__)

@database_routes.route('/reset_database', methods=['GET', 'POST'])
def reset_database():
    if request.method == 'POST':
        password = request.form.get('password')
        correct_password = os.environ.get('ADMIN_PASSWORD', 'password')
        if password == correct_password:
            database.reset_tables()
            flash("Database reset successfully.")
        else:
            return redirect("https://www.youtube.com/watch?v=xvFZjo5PgG0")
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
                flash("Teams uploaded successfully.")
            else:
                flash("No file selected.")
        else:
            return redirect("https://www.youtube.com/watch?v=xvFZjo5PgG0")
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
                flash("Tiles uploaded successfully.")
            else:
                flash("No file selected.")
        else:
            return redirect("https://www.youtube.com/watch?v=xvFZjo5PgG0")
    return render_template('upload_tiles.html')

@database_routes.route('/db_download', methods=['GET'])
def db_download():
    # Specify the directory where your database file is
    directory = os.getcwd()
    # Specify the name of your database file
    filename = 'my_database.db'
    return send_from_directory(directory, filename, as_attachment=True)
