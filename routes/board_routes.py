from flask import render_template, Blueprint
import math
from utils import autocomplete, database, db_entities

board_routes = Blueprint("board_routes", __name__)


@board_routes.route('/', methods=['GET'])
def index():
    teams = []
    for team in database.get_teams():
        teams.append(db_entities.Team(team))

    tiles = []
    for tile in database.get_tiles():
        tiles.append(db_entities.Tile(tile))

    return render_template('board.html', teams=teams, tiles=tiles, teamnames=autocomplete.team_names(), boardsize=get_board_size(), tilenames=autocomplete.tile_names())


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

    return render_template('board.html', teams=teams, tiles=tiles, teamname=team_name,
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