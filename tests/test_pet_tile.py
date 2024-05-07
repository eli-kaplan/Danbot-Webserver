import pytest

import database
import db_entities
from main import create_app
from routes import dink
from utils.spoof_pet import spoof_pet


@pytest.fixture()
def app():
    app = create_app()
    # other setup can go here
    database.reset_tables()
    yield app
    # clean up / reset resources here

@pytest.fixture()
def client(app):
    return app.test_client()

def test_single_pet_drop(client):
    database.reset_tables()
    database.read_teams('tests/test_csvs/default_team_1.csv')
    database.read_tiles('tests/test_csvs/default_tiles_4.csv')

    json_data = spoof_pet("Danbis", "Lil-zuk")
    result = dink.parse_pet(json_data, None)

    assert result == True

    team = database.get_team_by_id(1)
    team = db_entities.Team(team)
    assert round(team.team_points, 2) == round(0.5, 2)

    player_danbis = database.get_player_by_name("Danbis")
    player_danbis = db_entities.Player(player_danbis)
    assert player_danbis.tiles_completed == 0.5

def test_two_pet_drops(client):
    database.reset_tables()
    database.read_teams('tests/test_csvs/default_team_1.csv')
    database.read_tiles('tests/test_csvs/default_tiles_4.csv')

    json_data = spoof_pet("Danbis", "Lil-zuk")
    result = dink.parse_pet(json_data, None)

    assert result == True

    team = database.get_team_by_id(1)
    team = db_entities.Team(team)
    assert round(team.team_points, 2) == round(0.5, 2)

    player_danbis = database.get_player_by_name("Danbis")
    player_danbis = db_entities.Player(player_danbis)
    assert round(player_danbis.tiles_completed, 2) == round(0.5, 2)

    json_data = spoof_pet("Danbis", "Lil-ryguy")
    result = dink.parse_pet(json_data, None)

    assert result == True

    team = database.get_team_by_id(1)
    team = db_entities.Team(team)
    assert round(team.team_points, 2) == round(1, 2)

    player_danbis = database.get_player_by_name("Danbis")
    player_danbis = db_entities.Player(player_danbis)
    assert round(player_danbis.tiles_completed, 2) == round(1, 2)

def test_two_pet_drops_different_players(client):
    database.reset_tables()
    database.read_teams('tests/test_csvs/default_team_1.csv')
    database.read_tiles('tests/test_csvs/default_tiles_4.csv')

    json_data = spoof_pet("Danbis", "Lil-zuk")
    result = dink.parse_pet(json_data, None)
    assert result == True

    team = database.get_team_by_id(1)
    team = db_entities.Team(team)
    assert round(team.team_points, 2) == round(0.5, 2)

    player_danbis = database.get_player_by_name("Danbis")
    player_danbis = db_entities.Player(player_danbis)
    assert round(player_danbis.tiles_completed, 2) == round(0.5, 2)

    json_data = spoof_pet("Deidera", "Lil-ryguy")
    result = dink.parse_pet(json_data, None)

    assert result == True

    team = database.get_team_by_id(1)
    team = db_entities.Team(team)
    assert round(team.team_points, 2) == round(1, 2)

    player_deidera = database.get_player_by_name("Deidera")
    player_deidera = db_entities.Player(player_deidera)
    assert round(player_deidera.tiles_completed, 2) == round(0.5, 2)