import os
from functools import wraps

from flask import request, render_template, Blueprint, flash, redirect, url_for, abort, current_app
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from routes import dink
from utils import database, db_entities
from utils.database import get_player_names, get_tile_names, get_tiles
from utils.spoofed_jsons.spoof_chat import spoof_chat
from utils.spoofed_jsons.spoof_drop import award_drop_json
from utils.spoofed_jsons.spoof_kc import kc_spoof_json
from utils.spoofed_jsons.spoof_pet import spoof_pet

admin_routes = Blueprint("admin_routes", __name__)
def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

@admin_routes.route('/', methods=['GET'])
@admin_required
def home():
    return render_template('admin_templates/admin_home.html')


@admin_routes.route('/submit_a_tile', methods=['GET', 'POST'])
@admin_required
def submit_a_tile():
    tile_types = {}
    tile_triggers = {}
    tiles = get_tiles()  # Adjusted to your function to get all tiles
    for tile in tiles:
        tile = db_entities.Tile(tile)
        tile_triggers[tile.tile_name] = []
        tile_types[tile.tile_name] = tile.tile_type
        if tile.tile_type != 'PET':
            for x in tile.tile_triggers.split(','):
                for trigger in x.split('/'):
                    tile_triggers[tile.tile_name].append(trigger.strip())

    if request.method == 'GET':
        return render_template('admin_templates/submit_a_tile.html', player_names=get_player_names(),
                               tile_names=get_tile_names(), tile_triggers=tile_triggers, tile_types=tile_types)

    if request.method == 'POST':
        player_names = get_player_names()
        tile_names = get_tile_names()

        # Handle the image file upload
        tile_type = tile_types[request.form['tile_name']]
        image_file = request.files.get('image')
        if tile_type == 'DROP' or tile_type == 'SET':
            json = award_drop_json(
                request.form['ign'],
                request.form['event_to_trigger'],
                int(request.form['value']),
                int(request.form['quantity'])
            )
            # Pass the image path to your parsing function or handle it accordingly
            dink.parse_loot(json, image_file)

        elif tile_type == 'KILLCOUNT':
            json = kc_spoof_json(
                request.form['ign'],
                request.form['event_to_trigger'],
                int(request.form['quantity'])
            )

            dink.parse_kill_count(json, image_file)

        elif tile_type == 'PET':
            json = spoof_pet(
                request.form['ign'],
                request.form['event_to_trigger']
            )

            dink.parse_pet(json, image_file)

        elif tile_type == 'CHAT':
            json = spoof_chat(
                request.form['ign'],
                request.form['event_to_trigger']
            )

            dink.parse_chat(json, image_file)

        elif tile_type == 'NICHE':
            flash("I'm still deciding how to deal with niche tile submission")
            return render_template('admin_templates/submit_a_tile.html', player_names=player_names,
                                   tile_names=tile_names, tile_triggers=tile_triggers, tile_types=tile_types)

        flash("Data submitted! Check the relevant Discord channel and make sure it shows up.")
        return render_template('admin_templates/submit_a_tile.html', player_names=player_names,
                               tile_names=tile_names, tile_triggers=tile_triggers, tile_types=tile_types)

@admin_routes.route('/reset_database', methods=['GET', 'POST'])
@admin_required
def reset_database():
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('home'))
    if request.method == 'POST':
        database.reset_tables()
        flash("Database reset successfully.")
    return render_template('admin_templates/reset_database.html')


@admin_routes.route('/start_tracking', methods=['GET', 'POST'])
@admin_required
def start_tracking():
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('home'))
    if request.method == 'POST':
        flash("Now tracking user data")
    return render_template('admin_templates/start_tracking.html')


@admin_routes.route('/stop_tracking', methods=['GET', 'POST'])
@admin_required
def stop_tracking():
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('home'))
    if request.method == 'POST':
        flash("No longer tracking user data")
    return render_template('admin_templates/stop_tracking.html')

@admin_routes.route('/hide_board', methods=['GET', 'POST'])
@admin_required
def hide_board():
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('home'))
    if request.method == 'POST':
        flash("Board will now be hidden. Uploading tiles will not change the visibility")
    return render_template('admin_templates/hide_board.html')

@admin_routes.route('/show_board', methods=['GET', 'POST'])
@admin_required
def show_board():
    if not current_user.is_admin:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('home'))
    if request.method == 'POST':
        flash("Board is now being show. Uploading tiles will not change the visibility")
    return render_template('admin_templates/show_board.html')
