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

def test_single_player_niche_progress(client):
    database.reset_tables()
    database.read_teams('test_csvs/default_team_1.csv')
    database.read_tiles('test_csvs/default_tiles_5.csv')

    database.add_manual_progress("Test Niche Tile", "Danbis", 1)
    assert database.get_manual_progress_by_tile_name_and_team_name("Test Niche Tile", "Team 1") == 1

def test_single_player_multiple_progress(client):
    database.reset_tables()
    database.read_teams('test_csvs/default_team_1.csv')
    database.read_tiles('test_csvs/default_tiles_5.csv')

    database.add_manual_progress("Test Niche Tile", "Danbis", 1)
    assert database.get_manual_progress_by_tile_name_and_team_name("Test Niche Tile", "Team 1") == 1

    database.add_manual_progress("Test Niche Tile", "Danbis", 1)
    assert database.get_manual_progress_by_tile_name_and_team_name("Test Niche Tile", "Team 1") == 2

    database.add_manual_progress("Test Niche Tile", "Danbis", 1)
    assert database.get_manual_progress_by_tile_name_and_team_name("Test Niche Tile", "Team 1") == 3

    database.add_manual_progress("Test Niche Tile", "Danbis", 1)
    assert database.get_manual_progress_by_tile_name_and_team_name("Test Niche Tile", "Team 1") == 4

    database.add_manual_progress("Test Niche Tile", "Danbis", 1)
    assert database.get_manual_progress_by_tile_name_and_team_name("Test Niche Tile", "Team 1") == 5