from flask import Flask, request, render_template, Blueprint, flash, redirect, send_from_directory
from werkzeug.utils import secure_filename
import sqlite3
import os
import database
import db_entities
from utils import autocomplete, scapify

user_routes = Blueprint("user_routes", __name__)

@user_routes.route('/team/<team_name>')
def team(team_name):
    # Find team, if it doesn't exist make an empty none team
    try:
        team = database.get_team_by_name(team_name)
        team = db_entities.Team(team)
    except:
        team = db_entities.Team(("None", 0, None, -1))

    # Get drops table data
    drops_dict = {}
    for drop in database.get_drops_by_team_id(team.team_id):
        drop = db_entities.Drop(drop)
        if drop.drop_name in drops_dict:
            quantity = drops_dict[drop.drop_name][0]
            value = drops_dict[drop.drop_name][1]
            drops_dict[drop.drop_name] = (quantity + drop.drop_quantity, value + (drop.drop_value * drop.drop_quantity))
        else:
            drops_dict[drop.drop_name] = (drop.drop_quantity, drop.drop_value * drop.drop_quantity)
    drops = []
    for key, value in drops_dict.items():
        drops.append((key, value[0], scapify.int_to_gp(value[1])))
    drops = sorted(drops, key=lambda drop: drop[2], reverse=True)
    drops = [(drop[0], drop[1], scapify.int_to_gp(drop[2])) for drop in drops]

    # Get killcount table data
    killcount_dict = {}
    for kc in database.get_killcount_by_team_id(team.team_id):
        kc = db_entities.Killcount(kc)
        if kc.boss_name in killcount_dict:
            killcount_dict[kc.boss_name] = killcount_dict[kc.boss_name] + kc.kills
        else:
            killcount_dict[kc.boss_name] = kc.kills
    killcount = []
    for key,value in killcount_dict.items():
        killcount.append((key, value))
    killcount = sorted(killcount, key=lambda kc: kc[1], reverse=True)

    most_deaths_player = None
    most_pets_player = None
    most_gold_player = None
    most_tiles_player = None

    most_deaths = 0
    most_pets = 0
    most_gold = 0
    most_tiles = 0

    total_gold = 0
    total_deaths = 0
    total_pets = 0
    total_tiles = 0

    players = []
    for player in database.get_players_by_team_id(team.team_id):
        player = db_entities.Player(player)
        players.append(player)

        total_gold += player.gp_gained
        total_deaths += player.deaths
        total_pets += player.pet_count
        total_tiles += player.tiles_completed

        if player.tiles_completed >= most_tiles:
            most_tiles = player.tiles_completed
            most_tiles_player = player
        if player.gp_gained >= most_gold:
            most_gold = player.gp_gained
            most_gold_player = player
        if player.pet_count >= most_pets:
            most_pets = player.pet_count
            most_pets_player = player
        if player.deaths >= most_deaths:
            most_deaths = player.deaths
            most_deaths_player = player

        player.gp_gained = scapify.int_to_gp(player.gp_gained)
    players = sorted(players, key=lambda player: player.tiles_completed, reverse=True)

    return render_template('team.html', team=team, players=players, most_tiles_player=most_tiles_player,
                           most_gold_player=most_gold_player, most_pets_player=most_pets_player,
                           most_deaths_player=most_deaths_player, drops=drops,
                           total_pets=total_pets, total_tiles=total_tiles, total_gold=scapify.int_to_gp(total_gold),
                           total_deaths=total_deaths, teamnames=autocomplete.team_names())

@user_routes.route('/player/<player_name>')
def player(player_name):
    player = database.get_player_by_name(player_name)
    try:
        player = db_entities.Player(player)
        team = database.get_team_by_id(player.team_id)
        team = db_entities.Team(team)
    except:
        player = db_entities.Player((-1, "None", 0, 0, 0, -1, 0, 0))
        team = db_entities.Team(("None", 0, None, -1))

    player.gp_gained = scapify.int_to_gp(player.gp_gained)

    drops_dict = {}
    for drop in database.get_drops_by_player_id(player.player_id):
        drop = db_entities.Drop(drop)
        if drop.drop_name in drops_dict:
            quantity = drops_dict[drop.drop_name][0]
            value = drops_dict[drop.drop_name][1]
            drops_dict[drop.drop_name] = (quantity + drop.drop_quantity, value + (drop.drop_value * drop.drop_quantity))
        else:
            drops_dict[drop.drop_name] = (drop.drop_quantity, drop.drop_value * drop.drop_quantity)

    drops = []
    for key, value in drops_dict.items():
        drops.append((key, value[0], value[1]))
    drops = sorted(drops, key=lambda drop: drop[2], reverse=True)
    drops = [(drop[0], drop[1], scapify.int_to_gp(drop[2])) for drop in drops]

    killcount = []
    for kc in database.get_killcount_by_player_id(player.player_id):
        kc = db_entities.Killcount(kc)
        killcount.append(kc)
    killcount = sorted(killcount, key=lambda kc: kc.kills, reverse=True)


    return render_template('player.html', player=player, drops=drops, killcount=killcount, team=team, playernames=autocomplete.player_names())


@user_routes.route('/leaderboard', methods=['GET'])
def leaderboard():
    most_deaths_player = None
    most_pets_player = None
    most_gold_player = None
    most_tiles_player = None

    most_deaths = 0
    most_pets = 0
    most_gold = 0
    most_tiles = 0

    total_gold = 0
    total_deaths = 0
    total_pets = 0
    total_tiles = 0

    players = []
    for player in database.get_players():
        player = db_entities.Player(player)
        players.append(player)

        total_gold += player.gp_gained
        total_deaths += player.deaths
        total_pets += player.pet_count
        total_tiles += player.tiles_completed

        if player.tiles_completed >= most_tiles:
            most_tiles = player.tiles_completed
            most_tiles_player = player
        if player.gp_gained >= most_gold:
            most_gold = player.gp_gained
            most_gold_player = player
        if player.pet_count >= most_pets:
            most_pets = player.pet_count
            most_pets_player = player
        if player.deaths >= most_deaths:
            most_deaths = player.deaths
            most_deaths_player = player

        player.gp_gained = scapify.int_to_gp(player.gp_gained)

    players = sorted(players, key=lambda player: player.tiles_completed, reverse=True)

    teams = []
    for team in database.get_teams():
        teams.append(db_entities.Team(team))

    teams = sorted(teams, key=lambda team: team.team_points, reverse=True)

    return render_template('leaderboard.html', teams=teams, players=players, most_tiles_player=most_tiles_player,
                           most_gold_player=most_gold_player, most_pets_player=most_pets_player,
                           most_deaths_player=most_deaths_player,
                           total_pets=total_pets, total_tiles=total_tiles, total_gold=scapify.int_to_gp(total_gold),
                           total_deaths=total_deaths)
