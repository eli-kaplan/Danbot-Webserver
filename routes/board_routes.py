from collections import defaultdict

from flask import render_template, Blueprint
import math
from utils import autocomplete, database, db_entities

board_routes = Blueprint("board_routes", __name__)

@board_routes.route('/compare', methods=['GET'])
def compare():
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
        completed_tile = db_entities.Completed_Tile(completed_tile)
        completed_tiles[completed_tile.tile_id][completed_tile.team_id] = completed_tiles[completed_tile.tile_id][completed_tile.team_id] + 1

    partial_tiles = defaultdict(lambda: defaultdict(int))
    for partial_tile in database.get_partial_completions():
        partial_tile = db_entities.PartialCompletion(partial_tile)
        partial_tiles[partial_tile.tile_id][partial_tile.team_id] = round(partial_tiles[partial_tile.tile_id][partial_tile.team_id] + partial_tile.partial_completion, 2)



    return render_template('board_templates/compare.html', teams=teams, tiles=tiles, completed_tiles=completed_tiles, partial_tiles=partial_tiles)

@board_routes.route('/', methods=['GET'])
def index():
    teams = []
    for team in database.get_teams():
        teams.append(db_entities.Team(team))

    tiles = []
    for tile in database.get_tiles():
        tiles.append(db_entities.Tile(tile))

    return render_template('board_templates/board.html', teams=teams, tiles=tiles, teamnames=autocomplete.team_names(), boardsize=get_board_size(), tilenames=autocomplete.tile_names())


@board_routes.route('/<team_name>', methods=['GET'])
def board(team_name):
    # Find team, if it doesn't exist make an empty none team
    try:
        team = database.get_team_by_name(team_name)
        team = db_entities.Team(team)
    except:
        team = db_entities.Team(("None", 0, None, -1))

    # get list of teams for the dropdown menu
    teams = []
    for t in database.get_teams():
        teams.append(db_entities.Team(t))

    # get tiles for board population
    tiles = []
    for tile in database.get_tiles():
        tiles.append(db_entities.Tile(tile))

    return render_template('board_templates/board.html', teams=teams, tiles=tiles, teamname=team_name,
                           teamnames=autocomplete.team_names(),boardsize=get_board_size(), tilenames=autocomplete.tile_names())


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