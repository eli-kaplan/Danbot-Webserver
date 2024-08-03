from flask import request, render_template, Blueprint, flash, redirect
from werkzeug.utils import secure_filename
import os
from utils import database

admin_routes = Blueprint("admin_routes", __name__)

@admin_routes.route('/', methods=['GET'])
def home():
    return render_template('admin_templates/admin_home.html')

@admin_routes.route('/reset_database', methods=['GET', 'POST'])
def reset_database():
    if request.method == 'POST':
        password = request.form.get('password')
        correct_password = os.environ.get('ADMIN_PASSWORD', 'password')
        if password == correct_password:
            database.reset_tables()
            flash("Database reset successfully.")
        else:
            return redirect("https://www.youtube.com/watch?v=xvFZjo5PgG0")
    return render_template('admin_templates/reset_database.html')

@admin_routes.route('upload_teams', methods=['GET', 'POST'])
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
    return render_template('admin_templates/upload_teams.html')

@admin_routes.route('/upload_tiles', methods=['GET', 'POST'])
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
    return render_template('admin_templates/upload_tiles.html')


@admin_routes.route('/start_tracking', methods=['GET', 'POST'])
def start_tracking():
    if request.method == 'POST':
        password = request.form.get('password')
        correct_password = os.environ.get('ADMIN_PASSWORD', 'password')
        if password == correct_password:
            os.environ['TRACKING'] = "TRUE"
            flash("Now tracking user data")
        else:
            return redirect("https://www.youtube.com/watch?v=xvFZjo5PgG0")
    return render_template('admin_templates/start_tracking.html')

@admin_routes.route('/stop_tracking', methods=['GET', 'POST'])
def stop_tracking():
    if request.method == 'POST':
        password = request.form.get('password')
        correct_password = os.environ.get('ADMIN_PASSWORD', 'password')
        if password == correct_password:
            os.environ['TRACKING'] = "FALSE"
            flash("No longer tracking user data")
        else:
            return redirect("https://www.youtube.com/watch?v=xvFZjo5PgG0")
    return render_template('admin_templates/stop_tracking.html')