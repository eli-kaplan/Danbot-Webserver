import os
import csv
import psycopg2

import utils.db_entities as db_entities
from utils.db_entities import Player, Tile


def connect():
    return psycopg2.connect(dbname=os.getenv('PGDATABASE'), user=os.getenv('PGUSER'), password=os.getenv('PGPASSWORD'),
                            host=os.getenv('PGHOST'), port=os.getenv('PGPORT'))


def add_team_points(team_id, team_points):
    with connect() as conn:
        cursor = conn.cursor()
        update_query = '''
            UPDATE teams
            SET team_points = team_points + %s
            WHERE team_id = %s
        '''
        cursor.execute(update_query, (team_points, team_id,))

def rename_team(old_team_name, new_team_name):
    with connect() as conn:
        cursor = conn.cursor()
        update_query = '''
            UPDATE teams
            SET team_name = %s
            WHERE team_name = %s
            '''
        cursor.execute(update_query, (new_team_name, old_team_name,))

# Functions for 'teams' table
def add_team(team_name, team_points, team_webhook):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO teams (team_name, team_points, team_webhook) VALUES (%s, %s, %s)",
                       (team_name, team_points, team_webhook))
        return cursor.execute("SELECT team_id from teams where team_name = %s", (team_name,))


def remove_team(team_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM teams WHERE team_id = %s", (team_id,))


def get_teams():
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM teams")
        return cursor.fetchall()


def get_team_by_id(team_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM teams where team_id = %s", (team_id,))
        return cursor.fetchone()


def get_team_by_name(team_name):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM teams where team_name = %s", (team_name,))
        return cursor.fetchone()


# Functions for 'players' table
def add_player(player_name, deaths, gp_gained, tiles_completed, team_id, pet_count):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO players (player_name, deaths, gp_gained, tiles_completed, team_id, pet_count) VALUES (%s, %s, %s, %s, %s, %s)",
            (player_name, deaths, gp_gained, tiles_completed, team_id, pet_count))


def add_death_by_playername(rsn):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE players SET deaths = deaths + 1 WHERE player_name = %s", (rsn,))


def add_pet_by_playername(rsn):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE players SET pet_count = pet_count + 1 WHERE player_name = %s", (rsn,))


def add_player_tile_completions(player_id, tiles_completed):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE players
            SET tiles_completed = tiles_completed + %s
            WHERE player_id = %s
        ''', (tiles_completed, player_id))


def rename_player(old_player_name, new_player_name):
    with connect() as conn:
        cursor = conn.cursor()
        update_query = '''
            UPDATE players
            SET player_name = %s
            WHERE player_name = %s
            '''
        cursor.execute(update_query, (new_player_name, old_player_name,))




def remove_player(player_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM players WHERE player_id = %s", (player_id,))


def get_players():
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM players")
        return cursor.fetchall()


def get_players_by_team_id(team_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM players WHERE team_id = %s", (team_id,))
        return cursor.fetchall()


def get_player_by_name(player_name):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM players where player_name = %s", (player_name,))
        return cursor.fetchone()


def get_player_by_id(player_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM players where player_id = %s", (player_id,))
        return cursor.fetchone()


# Functions for 'drops' table
def add_drop(team_id, player_id, player_name, drop_name, drop_value, drop_quantity, drop_source):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO drops (team_id, player_id, player_name, drop_name, drop_value, drop_quantity, drop_source) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (team_id, player_id, player_name, drop_name, drop_value, drop_quantity, drop_source))
        cursor.execute("UPDATE Players SET gp_gained = gp_gained + %s WHERE player_id = %s",
                       (drop_value * drop_quantity, player_id))


def remove_drop(player_id, drop_name):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM drops WHERE player_id = %s AND drop_name = %s", (player_id, drop_name))


def get_drops():
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM drops")
        return cursor.fetchall()


def get_drops_by_team_id(team_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM drops WHERE team_id = %s", (team_id,))
        return cursor.fetchall()


def get_drops_by_player_id(player_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM drops WHERE player_id = %s", (player_id,))
        return cursor.fetchall()


# Functions for 'killcount' table
def add_killcount(player_id, team_id, boss_name, kills):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO killcount (player_id, team_id, boss_name, kills) VALUES (%s, %s, %s, %s)",
                       (player_id, team_id, boss_name, kills))


def remove_killcount(player_id, boss_name):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM killcount WHERE player_id = %s AND boss_name = %s", (player_id, boss_name))


def get_killcounts():
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM killcount")
        return cursor.fetchall()


# Functions for 'drop_whitelist' table
def add_drop_whitelist(drop_name, tile_id):
    with connect() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO drop_whitelist (drop_name, tile_id) VALUES (%s, %s)",
                           (drop_name, tile_id,))
        except:
            print("Warning! Duplicate trigger found! " + drop_name)


def remove_drop_whitelist(drop_name):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM drop_whitelist WHERE drop_name = %s", (drop_name,))


def get_drop_whitelist():
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM drop_whitelist")
        return cursor.fetchall()


def get_drop_whitelist_by_item_name(item_name):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM drop_whitelist WHERE drop_name = %s", (item_name,))
        return cursor.fetchone()


# Functions for 'completed_tiles' table
def add_completed_tile(tile_id, team_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO completed_tiles (tile_id, team_id) VALUES (%s, %s)",
                       (tile_id, team_id))


def remove_completed_tile(tile_id, team_id):
    with connect() as conn:
        cursor = conn.cursor()
        completed_tile = db_entities.CompletedTile(
            cursor.execute("SELECT * FROM completed_tiles WHERE tile_name = %s and team_id = %s",
                           (tile_id, team_id)).fetchone())
        cursor.execute("DELETE FROM completed_tiles WHERE completed_tile_pk = %s", (completed_tile.completed_tile_pk))


def get_completed_tiles():
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM completed_tiles")
        return cursor.fetchall()


def get_completed_tiles_by_team_id_and_tile_id(team_id, tile_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM completed_tiles where team_id = %s and tile_id = %s", (team_id, tile_id))
        return cursor.fetchall()


def add_tile(tile_name, tile_type, tile_triggers, tile_trigger_weights, tile_unique_drops, tile_triggers_required,
             tile_repetition, tile_points):
    with connect() as conn:
        cursor = conn.cursor()
        if tile_unique_drops == "N/A" or tile_unique_drops == "":
            tile_unique_drops = "FALSE"
        if tile_triggers_required == "N/A" or tile_triggers_required == "":
            tile_triggers_required = 0

        cursor.execute(
            "INSERT INTO tiles (tile_name, tile_type, tile_triggers, tile_trigger_weights, tile_unique_drops, tile_triggers_required, tile_repetition, tile_points) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (tile_name, tile_type, tile_triggers, tile_trigger_weights, tile_unique_drops, tile_triggers_required,
             tile_repetition, tile_points))


# ... Repeat similar functions for 'drops', 'killcount', 'drop_whitelist', and 'completed_tiles' tables ...

def get_tiles():
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tiles")
        return cursor.fetchall()


def get_niche_tiles():
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tiles WHERE tile_type = %s", ("NICHE",))
        return cursor.fetchall()


def get_tile_by_drop(drop_name):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM drop_whitelist where drop_name = %s", (drop_name,))
        try:
            tile_id = cursor.fetchone()[1]
        except:
            return None
        cursor.execute("SELECT * FROM tiles where tile_id = %s", (tile_id,))
        return cursor.fetchone()

def get_tile_by_id(tile_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tiles where tile_id = %s", (tile_id,))
        return cursor.fetchone()

def get_tile_by_name(tile_name):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tiles where tile_name = %s", (tile_name,))
        return cursor.fetchone()


def get_drops_by_item_name_and_team_id(item_name, team_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM drops where team_id = %s and drop_name = %s", (team_id, item_name,))
        return cursor.fetchall()


# Functions for 'killcount' table
def add_killcount(player_id, team_id, bossname, kills):
    with connect() as conn:
        cursor = conn.cursor()

        # Check if the row already exists
        cursor.execute("SELECT * FROM KillCount WHERE player_id = %s AND team_id = %s AND boss_name = %s",
                       (player_id, team_id, bossname))
        row = cursor.fetchone()

        if row is not None:
            # If the row exists, update the kills
            cursor.execute(
                "UPDATE KillCount SET kills = kills + %s WHERE player_id = %s AND team_id = %s AND boss_name = %s",
                (kills, player_id, team_id, bossname))
        else:
            # If the row doesn't exist, insert a new row
            cursor.execute("INSERT INTO KillCount (player_id, team_id, boss_name, kills) VALUES (%s, %s, %s, %s)",
                           (player_id, team_id, bossname, kills))

        # Commit the changes
        conn.commit()

def get_partial_completions():
    with connect() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM partial_completions")
        return cursor.fetchall()

def add_player_partial_completions(player_id, team_id, tile_id, value):
    with connect() as conn:
        cursor = conn.cursor()

        # Check if the row already exists
        cursor.execute("SELECT * FROM partial_completions WHERE player_id = %s AND team_id = %s AND tile_id = %s",
                       (player_id, team_id, tile_id))
        row = cursor.fetchone()

        if row is not None:
            # If the row exists, update the kills
            cursor.execute(
                "UPDATE partial_completions SET partial_completion = partial_completion + %s WHERE player_id = %s AND team_id = %s AND tile_id = %s",
                (value, player_id, team_id, tile_id))
        else:
            cursor.execute("INSERT INTO partial_completions (player_id, team_id, tile_id, partial_completion) VALUES (%s, %s, %s, %s)",
                           (player_id, team_id, tile_id, value))

        conn.commit()

def get_partial_completions_by_team_id_and_tile_id(team_id, tile_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM partial_completions WHERE team_id = %s AND tile_id = %s", (team_id, tile_id))
        return cursor.fetchall()

def get_partial_completions_by_team_id(team_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM partial_completions WHERE team_id = %s", (team_id,))
        return cursor.fetchall()

def get_partial_completions_by_player_id(player_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM partial_completions WHERE player_id = %s", (player_id,))
        return cursor.fetchall()

def remove_partial_completion(partial_completion_pk):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM partial_completions WHERE partial_completion_pk = %s", (partial_completion_pk,))

def get_killcount_by_team_id_and_boss_name(team_id, boss_name):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM killcount WHERE team_id = %s AND boss_name = %s", (team_id, boss_name))
        return cursor.fetchall()


def get_killcount_by_team_id(team_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM killcount WHERE team_id = %s", (team_id,))
        return cursor.fetchall()


def get_killcount_by_player_id(player_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM killcount WHERE player_id = %s", (player_id,))
        return cursor.fetchall()


def add_manual_progress(tile_name, player_name, progress):
    with connect() as conn:
        cursor = conn.cursor()

        # Find the player
        cursor.execute("SELECT * FROM players WHERE player_name = %s", (player_name,))
        player = db_entities.Player(cursor.fetchone())

        # Find the team
        cursor.execute("SELECT * FROM teams where team_id = %s", (player.team_id,))
        team = db_entities.Team(cursor.fetchone())

        # Find the tile
        cursor.execute("SELECT * FROM tiles WHERE tile_name = %s", (tile_name,))
        tile = db_entities.Tile(cursor.fetchone())

        # Check if the row already exists
        cursor.execute("SELECT * FROM manual_tile_progress WHERE team_id = %s AND tile_id = %s AND player_id = %s",
                       (team.team_id, tile.tile_id, player.player_id))
        row = cursor.fetchone()

        if row is not None:
            # If the row exists, update the kills
            cursor.execute(
                "UPDATE manual_tile_progress SET progress = progress + %s WHERE team_id = %s AND tile_id = %s AND player_id = %s",
                (progress, team.team_id, tile.tile_id, player.player_id))
        else:
            # If the row doesn't exist, insert a new row
            cursor.execute("INSERT INTO manual_tile_progress (tile_id, team_id, progress, player_id) VALUES (%s, %s, %s, %s)",
                           (tile.tile_id, team.team_id, progress, player.player_id))


def get_manual_progress_by_tile_name_and_team_name(tile_name, team_name):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM teams where team_name = %s", (team_name,))
        team = db_entities.Team(cursor.fetchone())

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tiles where tile_name = %s", (tile_name,))
        tile = db_entities.Tile(cursor.fetchone())

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM manual_tile_progress WHERE team_id = %s AND tile_id = %s",
                       (team.team_id, tile.tile_id,))
        try:
            return cursor.fetchone()[2]
        except:
            return 0


def get_manual_progress_by_tile_id_and_team_id(tile_id, team_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM manual_tile_progress WHERE team_id = %s and tile_id = %s", (team_id, tile_id,))
        try:
            return cursor.fetchone()[2]
        except:
            return 0


def add_request(team_name, evidence):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO requests (team_name, evidence) VALUES (%s, %s)", (team_name, evidence,))


def get_request():
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM requests")
        return cursor.fetchone()


def delete_request(request_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM requests WHERE request_id = %s", (request_id,))


def add_chats(player_id, team_id, tile_id, chat):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO chats (player_id, team_id, tile_id, chat) VALUES (%s, %s, %s, %s)", (player_id, team_id, tile_id, chat))


def get_chats(chats_pk):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chats WHERE chats_pk = %s", (chats_pk,))
        return cursor.fetchall()


def get_chats_by_player_id_and_tile_id(player_id, tile_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chats WHERE player_id = %s and tile_id = %s", (player_id, tile_id))
        return cursor.fetchall()


def get_chats_by_team_id_and_tile_id(team_id, tile_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chats WHERE team_id = %s and tile_id = %s", (team_id, tile_id))
        return cursor.fetchall()


def delete_chat(chats_pk):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chats WHERE chats_pk = %s", (chats_pk,))

def add_relevant_drop(team_id, player_id, tile_id, tile_name, drop_name, player_name):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO relevant_drops (team_id, player_id, tile_id, tile_name, drop_name, player_name)
            VALUES (%s, %s, %s, %s, %s, %s)
            ''', (team_id, player_id, tile_id, tile_name, drop_name, player_name))
        conn.commit()

def get_relevant_drop_by_player_id(player_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM relevant_drops WHERE player_id = %s", (player_id,))
        return cursor.fetchall()

def get_relevant_drop_by_team_id(team_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM relevant_drops WHERE team_id = %s", (team_id,))
        return cursor.fetchall()

def get_relevant_drop_by_team_id_and_tile_id(team_id, tile_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM relevant_drops WHERE team_id = %s AND tile_id = %s", (team_id, tile_id,))
        return cursor.fetchall()

def delete_relevant_drop(relevant_drops_pk):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM relevant_drops WHERE relevant_drops_pk = %s", (relevant_drops_pk,))
        conn.commit()


def change_player_team(player_id, new_team_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE chats SET team_id = %s WHERE player_id = %s", (new_team_id, player_id,))
        cursor.execute("UPDATE drops SET team_id = %s WHERE player_id = %s", (new_team_id, player_id,))
        cursor.execute("UPDATE killcount SET team_id = %s WHERE player_id = %s", (new_team_id, player_id,))
        cursor.execute("UPDATE partial_completions SET team_id = %s WHERE player_id = %s", (new_team_id, player_id,))
        cursor.execute("UPDATE relevant_drops SET team_id = %s WHERE player_id = %s", (new_team_id, player_id,))
        cursor.execute("UPDATE players SET team_id = %s WHERE player_id = %s", (new_team_id, player_id,))
        cursor.execute("UPDATE manual_tile_progress SET team_id = %s WHERE player_id = %s", (new_team_id, player_id,))
        conn.commit()


def reset_tables():
    # Drop all tables
    print("connecting to db")
    conn = connect()
    print("connected")
    cursor = conn.cursor()
    # Get the list of all tables
    cursor.execute(
        "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';")
    tables = cursor.fetchall()

    # Drop each table
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table[0]} CASCADE;")

    print("All tables dropped successfully.")
    print("Recreating now...")

    # Create the 'drops' table

    cursor.execute('''
            CREATE TABLE teams (
                team_name text,
                team_points real,
                team_webhook text,
                team_id SERIAL PRIMARY KEY
            )
            ''')

    cursor.execute('''
            CREATE TABLE players (
                player_id SERIAL PRIMARY KEY,
                player_name text,
                deaths integer,
                gp_gained integer,
                tiles_completed real,
                team_id integer,
                pet_count integer,
                FOREIGN KEY(team_id) REFERENCES teams(team_id)
            )
            ''')

    cursor.execute('''
            CREATE TABLE drops (
                team_id integer,
                player_id integer,
                player_name text,
                drop_name text,
                drop_value real,
                drop_quantity integer,
                drop_source text,
                drops_pk SERIAL PRIMARY KEY,
                FOREIGN KEY(player_id) REFERENCES players(player_id),
                FOREIGN KEY(team_id) REFERENCES teams(team_id)
            )
        ''')

    cursor.execute('''
            CREATE TABLE killcount (
                player_id integer,
                team_id integer,
                boss_name text,
                kills integer,
                killcount_pk SERIAL PRIMARY KEY,
                FOREIGN KEY(player_id) REFERENCES players(player_id),
                FOREIGN KEY (team_id) REFERENCES teams(team_id)
            )''')

    cursor.execute('''
            CREATE TABLE tiles (
                tile_id SERIAL PRIMARY KEY,
                tile_name text,
                tile_type text,
                tile_triggers text,
                tile_trigger_weights text,
                tile_unique_drops boolean,
                tile_triggers_required int,
                tile_repetition int,
                tile_points real
            )
            ''')

    cursor.execute('''
            CREATE TABLE drop_whitelist (
                drop_name text PRIMARY KEY,
                tile_id int,
                FOREIGN KEY (tile_id) REFERENCES tiles(tile_id)
            )''')

    cursor.execute('''
            CREATE TABLE completed_tiles (
                team_id integer,
                tile_id integer,
                completed_tile_pk SERIAL PRIMARY KEY,
                FOREIGN KEY (tile_id) REFERENCES tiles(tile_id),
                FOREIGN KEY (team_id) REFERENCES teams(team_id)
            )
            ''')

    cursor.execute('''
            CREATE TABLE manual_tile_progress (
                player_id integer,
                team_id integer,
                tile_id integer,
                progress real,
                manual_tile_progress_pk SERIAL PRIMARY KEY,
                FOREIGN KEY (team_id) REFERENCES teams(team_id),
                FOREIGN KEY (tile_id) REFERENCES tiles(tile_id),
                FOREIGN KEY (player_id) REFERENCES players(player_id)
            )
            ''')

    cursor.execute('''
            CREATE TABLE requests (
                request_id SERIAL PRIMARY KEY,
                team_name text,
                evidence text
            )
            ''')

    cursor.execute('''
            CREATE TABLE chats (
                player_id integer,
                team_id integer,
                tile_id integer,
                chat text,
                chats_pk SERIAL PRIMARY KEY,
                FOREIGN KEY(team_id) REFERENCES teams(team_id),
                FOREIGN KEY(player_id) REFERENCES players(player_id),
                FOREIGN KEY(tile_id) REFERENCES tiles(tile_id)                
            )
            ''')

    cursor.execute('''
            CREATE TABLE partial_completions (
                team_id integer,
                tile_id integer,
                player_id integer,
                partial_completion real,
                partial_completion_pk SERIAL PRIMARY KEY,
                FOREIGN KEY(team_id) REFERENCES teams(team_id),
                FOREIGN KEY(tile_id) REFERENCES tiles(tile_id),
                FOREIGN KEY(player_id) REFERENCES players(player_id)
            )
            ''')

    cursor.execute('''
            CREATE TABLE relevant_drops (
                team_id integer,
                player_id integer,
                tile_id integer,
                tile_name text,
                drop_name text,
                player_name text,
                relevant_drops_pk SERIAL PRIMARY KEY,
                FOREIGN KEY(team_id) REFERENCES teams(team_id),
                FOREIGN KEY(tile_id) REFERENCES tiles(tile_id),
                FOREIGN KEY(player_id) REFERENCES players(player_id)    
            )
            ''')

    # Save (commit) the changes
    conn.commit()
    print("Finished creating!")

    # Close the connection
    conn.close()


def read_tiles(file_name):
    tiles = []
    with open(file_name, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            tiles.append(row)

    for i in range(1, len(tiles)):
        whitelist_items = []
        tile = tiles[i]
        tile_name = tile[0]
        tile_type = tile[1]
        tile_triggers = tile[2]
        for a in tile_triggers.split('/'):
            for b in a.split(','):
                whitelist_items.append(b)
        tile_trigger_weights = tile[3]
        tile_unique_drops = tile[4]
        tile_triggers_required = tile[5]
        tile_repetition = tile[6]
        tile_points = tile[7]
        add_tile(tile_name, tile_type, tile_triggers, tile_trigger_weights, tile_unique_drops, tile_triggers_required,
                 tile_repetition, tile_points)
        tile = Tile(get_tile_by_name(tile_name))
        for item in whitelist_items:
            if item.strip() == "":
                continue
            add_drop_whitelist(item.strip(), tile.tile_id)


def read_teams(file_name):
    teams = []
    with open(file_name, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            teams.append(row)

    for i in range(1, len(teams)):
        team = teams[i]
        team_name = team[0]
        team_webhook = team[1]
        players = team[2:]
        add_team(team_name, 0, team_webhook)
        team_obj = db_entities.Team(get_team_by_name(team_name))
        for player in players:
            if player == "":
                continue
            add_player(player, 0, 0, 0, team_obj.team_id, 0)

    return teams


