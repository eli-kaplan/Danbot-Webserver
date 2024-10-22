from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint

from routes.admin.admin_routes import admin_required
from utils import db_entities, config, teampassword
from utils.database import add_team, get_teams, get_team_by_id, remove_team, rename_team, add_team_points, \
    update_team_webhook, get_players_by_team_id, remove_player, get_drops_by_team_id, remove_drop, remove_drop_by_pk, \
    get_partial_completions_by_team_id

import urllib

def get_team_board_url(team_metadata: tuple) -> str:
    """Calculates the password-protected board URL for a particular team

    Args:
        team_metadata (tuple): Team metadata

    Returns:
        str: Board URL
    """
    team_name = team_metadata[0]
    team_webhook_url = team_metadata[2]
    team_pw = teampassword.calculate_team_password(team_webhook_url)

    return f"https://{config.get_server_ip()}/board/{urllib.parse.quote(team_name)}?pw={team_pw}"

team_routes = Blueprint("team_routes", __name__)

@team_routes.route('/teams', methods=['GET'])
@admin_required
def team_list():
    teams = get_teams()
    return render_template(
        'admin_templates/team_templates/team_list.html', 
        teams=[t + (get_team_board_url(t),) for t in teams])

@team_routes.route('/teams/new', methods=['GET', 'POST'])
@admin_required
def create_team():
    if request.method == 'POST':
        team_name = request.form.get('team_name')
        team_webhook = request.form.get('team_webhook')

        add_team(team_name, 0, team_webhook)

        flash('Team created successfully!', 'success')
        return redirect(url_for('team_routes.team_list'))

    return render_template('admin_templates/team_templates/new_team_form.html')

@team_routes.route('/teams/edit/<int:team_id>', methods=['GET', 'POST'])
@admin_required
def edit_team(team_id):
    team = get_team_by_id(team_id)
    team = db_entities.Team(team)
    if request.method == 'POST':
        new_team_name = request.form.get('team_name')
        team_points = request.form.get('team_points', 0)
        team_webhook = request.form.get('team_webhook')

        # Renaming team
        rename_team(team.team_name, new_team_name)

        # Updating team points (add additional points or set new value)
        add_team_points(team_id, float(team_points) - team.team_points)

        # update webhook
        update_team_webhook(team_id, team_webhook)

        flash('Team updated successfully!', 'success')
        return redirect(url_for('team_routes.team_list'))

    return render_template('admin_templates/team_templates/edit_team.html', team=team)

@team_routes.route('/teams/delete/<int:team_id>', methods=['POST'])
@admin_required
def delete_team(team_id):
    remove_team(team_id)
    flash('Team deleted successfully!', 'success')
    return redirect(url_for('team_routes.team_list'))
