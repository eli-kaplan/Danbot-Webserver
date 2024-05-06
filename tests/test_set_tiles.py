import os
import sys

import pytest

import db_entities
from routes import dink

sys.path.insert(0, os.path.abspath('..'))
import database
from main import app, create_app
from utils import spoof_drop


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

def test_single_set_piece(client):
    database.reset_tables()
    database.read_teams('tests/test_csvs/default_team_1.csv')
    database.read_tiles('tests/test_csvs/default_tiles_2.csv')

    json_data = spoof_drop.item_spoof_json("Danbis", "Odium 1", 1)
    result = dink.parse_loot(json_data, None)
    assert result == True

    player = db_entities.Player(database.get_player_by_name("Danbis"))
    assert player.tiles_completed == 1/3

    team = db_entities.Team(database.get_team_by_id(1))
    assert team.team_points == 0


def test_standard_completion(client):
    database.reset_tables()
    database.read_teams('tests/test_csvs/default_team_1.csv')
    database.read_tiles('tests/test_csvs/default_tiles_2.csv')

    json_data = spoof_drop.item_spoof_json("Danbis", "Odium 1", 1)
    result = dink.parse_loot(json_data, None)
    assert result == True

    json_data = spoof_drop.item_spoof_json("Danbis", "Odium 2", 1)
    result = dink.parse_loot(json_data, None)
    assert result == True

    json_data = spoof_drop.item_spoof_json("Danbis", "Odium 3", 1)
    result = dink.parse_loot(json_data, None)
    assert result == True

    player = db_entities.Player(database.get_player_by_name("Danbis"))
    assert player.tiles_completed == 1

    team = db_entities.Team(database.get_team_by_id(1))
    assert team.team_points == 1

def test_cross_team_completion_failure(client):
    database.reset_tables()
    database.read_teams('tests/test_csvs/default_team_1.csv')
    database.read_tiles('tests/test_csvs/default_tiles_2.csv')

    json_data = spoof_drop.item_spoof_json("Danbis", "Odium 1", 1)
    result = dink.parse_loot(json_data, None)
    assert result == True

    json_data = spoof_drop.item_spoof_json("Max uwu", "Odium 2", 1)
    result = dink.parse_loot(json_data, None)
    assert result == True

    json_data = spoof_drop.item_spoof_json("Danbis", "Odium 3", 1)
    result = dink.parse_loot(json_data, None)
    assert result == True

    player = db_entities.Player(database.get_player_by_name("Danbis"))
    assert player.tiles_completed == 2/3

    team = db_entities.Team(database.get_team_by_id(1))
    assert team.team_points == 0

def test_overcompletion(client):
    database.reset_tables()
    database.read_teams('tests/test_csvs/default_team_1.csv')
    database.read_tiles('tests/test_csvs/default_tiles_2.csv')

    json_data = spoof_drop.item_spoof_json("Danbis", "Odium 1", 1)
    result = dink.parse_loot(json_data, None)
    assert result == True

    json_data = spoof_drop.item_spoof_json("Danbis", "Odium 2", 1)
    result = dink.parse_loot(json_data, None)
    assert result == True

    json_data = spoof_drop.item_spoof_json("Danbis", "Odium 3", 1)
    result = dink.parse_loot(json_data, None)
    assert result == True

    player = db_entities.Player(database.get_player_by_name("Danbis"))
    assert player.tiles_completed == 1

    team = db_entities.Team(database.get_team_by_id(1))
    assert team.team_points == 1

    json_data = spoof_drop.item_spoof_json("Danbis", "Odium 1", 1)
    result = dink.parse_loot(json_data, None)
    assert result == True

    json_data = spoof_drop.item_spoof_json("Danbis", "Odium 2", 1)
    result = dink.parse_loot(json_data, None)
    assert result == True

    json_data = spoof_drop.item_spoof_json("Danbis", "Odium 3", 1)
    result = dink.parse_loot(json_data, None)
    assert result == True

    player = db_entities.Player(database.get_player_by_name("Danbis"))
    assert round(player.tiles_completed, 2) == 1

    team = db_entities.Team(database.get_team_by_id(1))
    assert team.team_points == 1


def test_mix_and_match_completion(client):
    database.reset_tables()
    database.read_teams('tests/test_csvs/default_team_1.csv')
    database.read_tiles('tests/test_csvs/default_tiles_2.csv')

    json_data = spoof_drop.item_spoof_json("Danbis", "Odium 1", 1)
    result = dink.parse_loot(json_data, None)
    assert result == True

    json_data = spoof_drop.item_spoof_json("Danbis", "Mal 2", 1)
    result = dink.parse_loot(json_data, None)
    assert result == True

    json_data = spoof_drop.item_spoof_json("Danbis", "Odium 3", 1)
    result = dink.parse_loot(json_data, None)
    assert result == True

    player = db_entities.Player(database.get_player_by_name("Danbis"))
    assert player.tiles_completed == 1

    team = db_entities.Team(database.get_team_by_id(1))
    assert team.team_points == 0