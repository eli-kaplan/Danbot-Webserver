import pytest

import database
import db_entities
from main import create_app
from routes import dink
from utils import spoof_death


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

def test_three_deaths(client):
    database.reset_tables()
    database.read_teams('tests/test_csvs/default_team_1.csv')
    database.read_tiles('tests/test_csvs/default_tiles_1.csv')

    json_data = spoof_death.spoof_death("Danbis")
    result = dink.parse_death(json_data)
    assert result == True

    player_danbis = database.get_player_by_name("Danbis")
    player_danbis = db_entities.Player(player_danbis)
    assert player_danbis.deaths == 1

    json_data = spoof_death.spoof_death("Danbis")
    result = dink.parse_death(json_data)
    assert result == True

    player_danbis = database.get_player_by_name("Danbis")
    player_danbis = db_entities.Player(player_danbis)
    assert player_danbis.deaths == 2

    json_data = spoof_death.spoof_death("Danbis")
    result = dink.parse_death(json_data)
    assert result == True

    player_danbis = database.get_player_by_name("Danbis")
    player_danbis = db_entities.Player(player_danbis)
    assert player_danbis.deaths == 3

def test_different_player_name_deaths(client):
    database.reset_tables()
    database.read_teams('tests/test_csvs/default_team_1.csv')
    database.read_tiles('tests/test_csvs/default_tiles_1.csv')

    json_data = spoof_death.spoof_death("Danbis")
    result = dink.parse_death(json_data)
    assert result == True

    player_danbis = database.get_player_by_name("Danbis")
    player_danbis = db_entities.Player(player_danbis)
    assert player_danbis.deaths == 1

    json_data = spoof_death.spoof_death("Deidera")
    result = dink.parse_death(json_data)
    assert result == True

    player_deidera = database.get_player_by_name("Deidera")
    player_deidera = db_entities.Player(player_deidera)
    assert player_deidera.deaths == 1

    json_data = spoof_death.spoof_death("Danbis")
    result = dink.parse_death(json_data)
    assert result == True

    player_danbis = database.get_player_by_name("Danbis")
    player_danbis = db_entities.Player(player_danbis)
    assert player_danbis.deaths == 2