import discord
from fuzzywuzzy import process
import database
import db_entities


def tile_names():
    tile_names = []
    for tile in database.get_tiles():
        tile = db_entities.Tile(tile)
        tile_names.append(tile.tile_name)
    return tile_names

def niche_tile_names():
    niche_tile_names = []
    for tile in database.get_niche_tiles():
        niche_tile = db_entities.Tile(tile)
        niche_tile_names.append(niche_tile.tile_name)
    return niche_tile_names

def tile_names():
    tile_names = []
    for tile in database.get_tiles():
        tile = db_entities.Tile(tile)
        tile_names.append(tile.tile_name)
    return tile_names

def team_names():
    team_names = []
    for team in database.get_teams():
        team = db_entities.Team(team)
        team_names.append(team.team_name)
    return team_names

def player_names():
    player_names = []
    for player in database.get_players():
        player = db_entities.Player(player)
        player_names.append(player.player_name)
    return player_names

def fuzzy_autocomplete(ctx: discord.AutocompleteContext, choices):
    def get_matches(string, choices, limit=25):
        results = process.extract(string, choices, limit=limit)
        return results

    current = ctx.value
    if current == "": # Cannot fuzzy match an empty string
        return choices

    matches = get_matches(current.lower(), choices)
    good_matches = []

    for item in matches:
        if int(item[1]) > 70:
            good_matches.append(item[0])

    return good_matches


def drop_names():
    drop_names = []
    for drop in database.get_drop_whitelist():
        drop = db_entities.Drop_whitelist(drop)
        drop_names.append(drop.drop_name)
    return drop_names

def boss_names():
    return ["Abyssal Sire", "Alchemical Hydra", "Artio", "Barrows Chests", "Bryophyta", "Calvar\'ion", "Callisto",
            "Cerberus", "Chambers of Xeric", "Chambers of Xeric: Challenge Mode", "Chaos Elemental", "Chaos Fanatic",
            "Commander Zilyana", "Corporeal Beast", "Crazy Archaeologist", "Dagannoth Prime", "Dagannoth Rex",
            "Dagannoth Supreme", "Deranged Archaeologist", "Duke Sucellus", "General Graardor", "Giant Mole",
            "Grotesque Guardians", "Hespori", "Kalphite Queen", "King Black Dragon", "Kraken", "Kree'Arra",
            "K'ril Tsutsaroth", "Mimic", "Nex", "Nightmare", "Phosani's Nightmare", "Obor", "Phantom Muspah",
            "Sarachnis", "Scorpia", "Scurrius", "Skotizo", "Spindel", "Tempoross", "The Gauntlet",
            "The Corrupted Gauntlet", "Leviathan", "Whisperer", "Theatre of Blood",
            "Theatre of Blood: Hard Mode", "Thermonuclear Smoke Devil", "Tombs of Amascut",
            "Tombs of Amascut: Expert Mode", "TzKal-Zuk", "TzTok-Jad", "Vardorvis", "Venenatis", "Vet'ion", "Vorkath",
            "Wintertodt", "Zalcano", "Zulrah"]





