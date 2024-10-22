import os
from collections import defaultdict
import random

from flask import render_template, Blueprint, request, jsonify, make_response, redirect, url_for
from flask_login import current_user
import math
from utils import autocomplete, database, db_entities, bingo, board

board_routes = Blueprint("board_routes", __name__)

@board_routes.route('/compare', methods=['GET'])
def compare():
    if not board.is_board_globally_visible(current_user):
        return board.hidden_board()

    teams = []
    for team in database.get_teams():
        teams.append(db_entities.Team(team))
    # teams = sorted(teams, key=lambda team: team.team_id, reverse=True)


    tiles = []
    for tile in database.get_tiles():
        tiles.append(db_entities.Tile(tile))
    # tiles = sorted(tiles, key=lambda tile: tile.tile_id, reverse=True)


    completed_tiles = defaultdict(lambda: defaultdict(int))
    for completed_tile in database.get_completed_tiles():
        completed_tile = db_entities.CompletedTile(completed_tile)
        completed_tiles[completed_tile.tile_id][completed_tile.team_id] = completed_tiles[completed_tile.tile_id][completed_tile.team_id] + 1

    partial_tiles = defaultdict(lambda: defaultdict(int))
    for partial_tile in database.get_partial_completions():
        partial_tile = db_entities.PartialCompletion(partial_tile)
        partial_tiles[partial_tile.tile_id][partial_tile.team_id] = round(partial_tiles[partial_tile.tile_id][partial_tile.team_id] + partial_tile.partial_completion, 2)



    return render_template('board_templates/compare.html', teams=teams, tiles=tiles, completed_tiles=completed_tiles, partial_tiles=partial_tiles)

class PanelData:
    def __init__(self):
        self.progress = None
        self.completions = "Completions: 0"
        self.repetitions = None
        self.rules = None


@board_routes.route('/', methods=['GET'])
def index():
    if not board.is_board_globally_visible(current_user):
        return board.hidden_board()

    teams = []
    panelData = {}
    tile_id_to_name = {}


    for team in database.get_teams():
        teams.append(db_entities.Team(team))

    tiles = []
    for tile in database.get_tiles():
        tile = db_entities.Tile(tile)
        tiles.append(tile)
        pd = PanelData()
        pd.progress = "Progress: Please select a team to see your progress"
        pd.repetition = f"Repetition: {tile.tile_repetition}"
        pd.rules = f"Rules: {tile.tile_rules}"
        panelData[tile.tile_name] = pd
        tile_id_to_name[tile.tile_id] = tile.tile_name
    tiles = sorted(tiles, key=lambda tile: tile.tile_id)


    completed_tiles = []
    partial_tiles = []

    team_name = request.cookies.get('teamname')
    if team_name:
        return redirect(url_for('board_routes.render_board', team_name=team_name))
    else:
        team = database.get_teams()
        if len(team) > 0:
            team = team[0]
            team = db_entities.Team(team)
            return render_board(team.team_name)
        else:
            return render_template('board_templates/board.html', teams=teams, tiles=tiles, teamname=team_name, teamnames=autocomplete.team_names(), boardsize=get_board_size(), tilenames=autocomplete.tile_names(), completed_tiles=completed_tiles, partial_tiles=partial_tiles, panelData=panelData)


@board_routes.route('/get_progress', methods=['GET'])
def get_progress():
    tile_name = request.args.get('tileName')
    team_name = request.args.get('teamName')

    team = db_entities.Team(database.get_team_by_name(team_name))
    tile = db_entities.Tile(database.get_tile_by_name(tile_name))

    progress = bingo.get_progress(team.team_id, tile.tile_id)

    if progress is None:
        return jsonify("Please select a team to see your progress")

    return jsonify(progress.status_text)


@board_routes.route('/<team_name>', methods=['GET'])
def render_board(team_name):
    team_password = request.args.get('pw') or None
    authenticated_team = ""
    if team_password is not None:
        if not board.is_team_authenticated(team_password, team_name):
            return board.hidden_board()

        authenticated_team = team_name
    else:
        if not board.is_board_globally_visible(current_user):
            return board.hidden_board()

    panelData = {}
    tile_id_to_name = {}

    # Find team, if it doesn't exist make an empty none team
    try:
        team = database.get_team_by_name(team_name)
        team = db_entities.Team(team)
    except:
        team = db_entities.Team(("None", 0, None, -1))

    # get list of teams for the dropdown menu
    # If user is authenticated for a particular team, only show this team name
    # Otherwise (tiles are globally visible), show all
    teams = []
    if authenticated_team != "":
        teams.append(team)
    else:
        for t in database.get_teams():
            teams.append(db_entities.Team(t))

    # get tiles for board population
    tiles = []
    for tile in database.get_tiles():
        tile = db_entities.Tile(tile)
        tiles.append(tile)
        pd = PanelData()
        pd.repetition = f"Repetition: {tile.tile_repetition}"
        pd.rules = f"Rules: {tile.tile_rules}"
        panelData[tile.tile_name] = pd
        tile_id_to_name[tile.tile_id] = tile.tile_name

    tiles = sorted(tiles, key=lambda tile: tile.tile_id)

    completed_tiles = []
    tile_completions = defaultdict(int)
    for completed_tile in database.get_completed_tiles_by_team_id(team.team_id):
        completed_tile = db_entities.CompletedTile(completed_tile)
        tile_completions[completed_tile.tile_id] = tile_completions[completed_tile.tile_id] + 1
        tileName = tile_id_to_name[completed_tile.tile_id]
        panelData[tileName].completions = f"Completions: {tile_completions[completed_tile.tile_id]}"

    tile_progress = defaultdict(int)
    for partial_completion in database.get_partial_completions_by_team_id(team.team_id):
        partial_completion = db_entities.PartialCompletion(partial_completion)
        tile_progress[partial_completion.tile_id] = tile_progress[partial_completion.tile_id] + 1

    partial_tiles = []
    for tile in tiles:
        if tile_completions[tile.tile_id] >= tile.tile_repetition:
            completed_tiles.append(tile.tile_name)
        elif tile_completions[tile.tile_id] > 0 or tile_progress[tile.tile_id] > 0:
            partial_tiles.append(tile.tile_name)



    resp = make_response(render_template('board_templates/board.html', teams=teams, tiles=tiles, teamname=team_name,
                           teamnames=autocomplete.team_names(),boardsize=get_board_size(), tilenames=autocomplete.tile_names(), completed_tiles=completed_tiles, partial_tiles=partial_tiles, panelData=panelData))
    resp.set_cookie('teamname', team_name)
    return resp


def get_board_size():
    # get tiles for board population
    tiles = []
    for tile in database.get_tiles():
        tiles.append(db_entities.Tile(tile))


    board_size = 0
    try:
        board_size = math.ceil(float(math.sqrt(len(tiles))))
    except ValueError:
        # do nothing
        pass

    return board_size