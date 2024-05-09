from flask import Flask, request, render_template, Blueprint, flash, redirect, send_from_directory
from werkzeug.utils import secure_filename
import sqlite3
import os
import database
import db_entities
from utils import autocomplete

user_routes = Blueprint("user_routes", __name__)

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

    players = []
    for player in database.get_players():
        player = db_entities.Player(player)
        players.append(player)
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


    players = sorted(players, key=lambda player: player.tiles_completed, reverse=True)

    teams = []
    for team in database.get_teams():
        teams.append(db_entities.Team(team))

    teams = sorted(teams, key=lambda team: team.team_points, reverse=True)

    return render_template('leaderboard.html', teams=teams, players=players, most_tiles_player=most_tiles_player,
                           most_gold_player=most_gold_player, most_pets_player=most_pets_player, most_deaths_player=most_deaths_player)


