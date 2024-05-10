import pytest

from utils import database, db_entities
from main import create_app
from routes import dink
from utils.spoofed_jsons import spoof_chat


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

def test_single_chat(client):
    database.reset_tables()
    database.read_teams('test_csvs/default_team_1.csv')
    database.read_tiles('test_csvs/default_tiles_6.csv')

    json_data = spoof_chat.spoof_chat("Danbis", "You are victorious!")
    result = dink.parse_chat(json_data, None)
    assert result == True

    player = database.get_player_by_name("Danbis")
    player = db_entities.Player(player)
    assert round(player.tiles_completed, 2) == 1/5

def test_single_player_completion_chat(client):
    database.reset_tables()
    database.read_teams('test_csvs/default_team_1.csv')
    database.read_tiles('test_csvs/default_tiles_6.csv')

    for i in range(5):
        json_data = spoof_chat.spoof_chat("Danbis", "You are victorious!")
        result = dink.parse_chat(json_data, None)
        assert result == True

        player = database.get_player_by_name("Danbis")
        player = db_entities.Player(player)
        assert round(player.tiles_completed, 2) == (i + 1)/5

    team = database.get_team_by_id(player.team_id)
    team = db_entities.Team(team)
    assert team.team_points == 1

def test_multiplayer_completion_chat(client):
    database.reset_tables()
    database.read_teams('test_csvs/default_team_1.csv')
    database.read_tiles('test_csvs/default_tiles_6.csv')

    for i in range(2):
        json_data = spoof_chat.spoof_chat("Danbis", "You are victorious!")
        result = dink.parse_chat(json_data, None)
        assert result == True

        player = database.get_player_by_name("Danbis")
        player = db_entities.Player(player)
        assert round(player.tiles_completed,2) == (i + 1)/5

    for i in range(3):
        json_data = spoof_chat.spoof_chat("Deidera", "You are victorious!")
        result = dink.parse_chat(json_data, None)
        assert result == True

        player = database.get_player_by_name("Deidera")
        player = db_entities.Player(player)
        assert round(player.tiles_completed,2) == (i + 1)/5

    team = database.get_team_by_id(player.team_id)
    team = db_entities.Team(team)
    assert team.team_points == 1

def test_multiplayer_over_completion_chat(client):
    database.reset_tables()
    database.read_teams('test_csvs/default_team_1.csv')
    database.read_tiles('test_csvs/default_tiles_6.csv')

    for i in range(22):
        json_data = spoof_chat.spoof_chat("Danbis", "You are victorious!")
        result = dink.parse_chat(json_data, None)
        assert result == True

        player = database.get_player_by_name("Danbis")
        player = db_entities.Player(player)
        assert round(player.tiles_completed, 2) == (i + 1)/5

        team = database.get_team_by_id(player.team_id)
        team = db_entities.Team(team)
        assert round(team.team_points, 2) == ((i + 1) - ((i + 1) % 5))/5

    for i in range(8):
        json_data = spoof_chat.spoof_chat("Deidera", "You are victorious!")
        result = dink.parse_chat(json_data, None)
        if i >= 3:
            assert result == False
        else:
            assert result == True

        player = database.get_player_by_name("Deidera")
        player = db_entities.Player(player)
        assert round(player.tiles_completed, 2) == round(min((i + 1)/5, 3/5), 2)

    team = database.get_team_by_id(player.team_id)
    team = db_entities.Team(team)
    assert team.team_points == 5