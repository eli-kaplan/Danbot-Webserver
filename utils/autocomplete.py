import discord

import database
import db_entities

async def tile_names(ctx: discord.AutocompleteContext):
    tile_names = []
    for tile in database.get_tiles():
        tile = db_entities.Tile(tile)
        tile_names.append(tile.tile_name)
    return tile_names

async def team_names(ctx: discord.AutocompleteContext):
    team_names = []
    for team in database.get_teams():
        team = db_entities.Team(team)
        team_names.append(team.team_name)
    return team_names

async def player_names(ctx: discord.AutocompleteContext):
    player_names = []
    for player in database.get_players():
        player = db_entities.Player(player)
        player_names.append(player.player_name)
    return player_names

async def drop_names(ctx: discord.AutocompleteContext):
    drop_names = []
    for drop in database.get_drop_whitelist():
        drop = db_entities.Drop_whitelist(drop)
        drop_names.append(drop.drop_name)
    return drop_names

async def boss_names(ctx: discord.AutocompleteContext):
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
