import os
import sys

import pytest

import db_entities
from routes import dink

sys.path.insert(0, os.path.abspath('..'))
import database
from main import app, create_app
from utils import spoof_kc

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

def test_single_player_kc_completion(client):
    database.reset_tables()
    database.read_teams('tests/test_csvs/default_team_1.csv')
    database.read_tiles('tests/test_csvs/default_tiles_3.csv')

    for i in range(10):
        team = db_entities.Team(database.get_team_by_id(1))
        assert team.team_points == 0

        json_data = spoof_kc.kc_spoof_json("Danbis", "Vardorvis")
        result = dink.parse_kill_count(json_data, None)
        assert result == True

        player_danbis = db_entities.Player(database.get_player_by_name("Danbis"))
        assert round(player_danbis.tiles_completed, 2) == (i + 1 ) / 10

    team = db_entities.Team(database.get_team_by_id(1))
    assert team.team_points == 1

def test_multiplayer_kc_completion(client):
    database.reset_tables()
    database.read_teams('tests/test_csvs/default_team_1.csv')
    database.read_tiles('tests/test_csvs/default_tiles_3.csv')

    for i in range(4):
        team = db_entities.Team(database.get_team_by_id(1))
        assert team.team_points == 0

        json_data = spoof_kc.kc_spoof_json("Danbis", "Vardorvis")
        result = dink.parse_kill_count(json_data, None)
        assert result == True

        player_danbis = db_entities.Player(database.get_player_by_name("Danbis"))
        assert round(player_danbis.tiles_completed, 2) == round((i + 1 ) / 10, 2)

    for i in range(6):
        team = db_entities.Team(database.get_team_by_id(1))
        assert team.team_points == 0

        json_data = spoof_kc.kc_spoof_json("Deidera", "Vardorvis")
        result = dink.parse_kill_count(json_data, None)
        assert result == True

        player_deidera = db_entities.Player(database.get_player_by_name("Deidera"))
        assert round(player_deidera.tiles_completed, 2) == round((i + 1 ) / 10, 2)

    team = db_entities.Team(database.get_team_by_id(1))
    assert team.team_points == 1

def test_multiple_completions(client):

    database.reset_tables()
    database.read_teams('tests/test_csvs/default_team_1.csv')
    database.read_tiles('tests/test_csvs/default_tiles_3.csv')

    for i in range(10):
        team = db_entities.Team(database.get_team_by_id(1))
        assert team.team_points == 0

        json_data = spoof_kc.kc_spoof_json("Danbis", "Vardorvis")
        result = dink.parse_kill_count(json_data, None)
        assert result == True

        player_danbis = db_entities.Player(database.get_player_by_name("Danbis"))
        assert round(player_danbis.tiles_completed, 2) == round((i + 1 ) / 10, 2)

    team = db_entities.Team(database.get_team_by_id(1))
    assert team.team_points == 1

    for i in range(10):
        team = db_entities.Team(database.get_team_by_id(1))
        assert team.team_points == 1

        json_data = spoof_kc.kc_spoof_json("Danbis", "Vardorvis")
        result = dink.parse_kill_count(json_data, None)
        assert result == True

        player_danbis = db_entities.Player(database.get_player_by_name("Danbis"))
        assert round(player_danbis.tiles_completed, 2) == round((1 + (i + 1)/ 10), 2)

    team = db_entities.Team(database.get_team_by_id(1))
    assert team.team_points == 2

def test_multiple_completions_multiple_players(client):

    database.reset_tables()
    database.read_teams('tests/test_csvs/default_team_1.csv')
    database.read_tiles('tests/test_csvs/default_tiles_3.csv')

    for i in range(6):
        team = db_entities.Team(database.get_team_by_id(1))
        assert team.team_points == 0

        json_data = spoof_kc.kc_spoof_json("Danbis", "Vardorvis")
        result = dink.parse_kill_count(json_data, None)
        assert result == True

        player_danbis = db_entities.Player(database.get_player_by_name("Danbis"))
        assert round(player_danbis.tiles_completed, 2) == round((i + 1 ) / 10, 2)

    for i in range(4):
        team = db_entities.Team(database.get_team_by_id(1))
        assert team.team_points == 0

        json_data = spoof_kc.kc_spoof_json("Deidera", "Vardorvis")
        result = dink.parse_kill_count(json_data, None)
        assert result == True

        player_danbis = db_entities.Player(database.get_player_by_name("Deidera"))
        assert round(player_danbis.tiles_completed, 2) == round((i + 1 ) / 10, 2)

    team = db_entities.Team(database.get_team_by_id(1))
    assert team.team_points == 1

    for i in range(4):
        team = db_entities.Team(database.get_team_by_id(1))
        assert team.team_points == 1

        json_data = spoof_kc.kc_spoof_json("Deidera", "Vardorvis")
        result = dink.parse_kill_count(json_data, None)
        assert result == True

        player_danbis = db_entities.Player(database.get_player_by_name("Deidera"))
        assert round(player_danbis.tiles_completed, 2) == round((4 + i + 1 ) / 10, 2)

    for i in range(6):
        team = db_entities.Team(database.get_team_by_id(1))
        assert team.team_points == 1

        json_data = spoof_kc.kc_spoof_json("Danbis", "Vardorvis")
        result = dink.parse_kill_count(json_data, None)
        assert result == True

        player_danbis = db_entities.Player(database.get_player_by_name("Danbis"))
        assert round(player_danbis.tiles_completed, 2) == round((6 + (i + 1))/ 10, 2)

    team = db_entities.Team(database.get_team_by_id(1))
    assert team.team_points == 2

def test_single_player_overcompletion(client):
    database.reset_tables()
    database.read_teams('tests/test_csvs/default_team_1.csv')
    database.read_tiles('tests/test_csvs/default_tiles_3.csv')

    for i in range(30):
        json_data = spoof_kc.kc_spoof_json("Danbis", "Vardorvis")
        result = dink.parse_kill_count(json_data, None)
        assert result == True

        player_danbis = db_entities.Player(database.get_player_by_name("Danbis"))
        assert round(player_danbis.tiles_completed, 2) == round(min((i + 1 ) / 10, 2), 2)


    team = db_entities.Team(database.get_team_by_id(1))
    assert team.team_points == 2

def test_multiplayer_overcompletion(client):
    database.reset_tables()
    database.read_teams('tests/test_csvs/default_team_1.csv')
    database.read_tiles('tests/test_csvs/default_tiles_3.csv')

    for i in range(15):
        json_data = spoof_kc.kc_spoof_json("Danbis", "Vardorvis")
        result = dink.parse_kill_count(json_data, None)
        assert result == True

        player_danbis = db_entities.Player(database.get_player_by_name("Danbis"))
        assert round(player_danbis.tiles_completed, 2) == round(min((i + 1 ) / 10, 2), 2)

    team = db_entities.Team(database.get_team_by_id(1))
    assert team.team_points == 1

    for i in range(15):
        json_data = spoof_kc.kc_spoof_json("Deidera", "Vardorvis")
        result = dink.parse_kill_count(json_data, None)
        assert result == True

        player_danbis = db_entities.Player(database.get_player_by_name("Deidera"))
        assert round(player_danbis.tiles_completed, 2) == round(min((i + 1 ) / 10, 0.5), 2)

    team = db_entities.Team(database.get_team_by_id(1))
    assert team.team_points == 2