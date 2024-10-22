from collections import defaultdict

from flask import render_template, Blueprint
from utils import autocomplete, scapify, database, db_entities, board
from flask_login import current_user

user_routes = Blueprint("user_routes", __name__)

@user_routes.route('/team/<team_name>')
def team(team_name):
    if not board.is_board_globally_visible(current_user):
        return board.hidden_board()

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
        drops.append((key, value[0], value[1]))
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

    players = sorted(players, key=lambda player: (player.tiles_completed, player.gp_gained), reverse=True)
    for player in players:
        player.gp_gained = scapify.int_to_gp(player.gp_gained)

    player_partials = defaultdict(int)
    partial_tiles = 0
    for partial_completion in database.get_partial_completions_by_team_id(team.team_id):
        partial_completion = db_entities.PartialCompletion(partial_completion)
        partial_tiles += partial_completion.partial_completion
        player_partials[partial_completion.player_id] = player_partials[partial_completion.player_id] + partial_completion.partial_completion

    for key, value in player_partials.items():
        player_partials[key] = round(value, 2)

    for player in players:
        player.tiles_completed = round(player.tiles_completed, 2)

    partial_tiles = round(partial_tiles, 2)

    relevant_drops = []
    for relevant_drop in database.get_relevant_drop_by_team_id(team.team_id):
        relevant_drop = db_entities.RelevantDrop(relevant_drop)
        relevant_drops.append(relevant_drop)
    if len(relevant_drops) > 0:
        relevant_drops = sorted(relevant_drops, key=lambda relevant_drop: relevant_drop.tile_name, reverse=True)

    total_tiles = round(total_tiles, 2)

    return render_template('user_templates/team.html', team=team, players=players, most_tiles_player=most_tiles_player,
                           most_gold_player=most_gold_player, most_pets_player=most_pets_player,
                           most_deaths_player=most_deaths_player, drops=drops, killcount=killcount,
                           total_pets=total_pets, total_tiles=total_tiles, total_gold=scapify.int_to_gp(total_gold),
                           total_deaths=total_deaths, teamnames=autocomplete.team_names(), partial_tiles=partial_tiles,
                           player_partials=player_partials, relevant_drops=relevant_drops)



@user_routes.route('/player/<player_name>')
def player(player_name):
    if not board.is_board_globally_visible(current_user):
        return board.hidden_board()

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

    partial_completions = 0
    for partial_completion in database.get_partial_completions_by_player_id(player.player_id):
        partial_completion = db_entities.PartialCompletion(partial_completion)
        partial_completions += partial_completion.partial_completion
    player.tiles_completed = round(player.tiles_completed, 2)

    relevant_drops = []
    for relevant_drop in database.get_relevant_drop_by_player_id(player.player_id):
        relevant_drop = db_entities.RelevantDrop(relevant_drop)
        relevant_drops.append(relevant_drop)
    if len(relevant_drops) > 0:
        relevant_drops = sorted(relevant_drops, key=lambda relevant_drop: relevant_drop.tile_name, reverse=True)

    return render_template('user_templates/player.html', player=player, drops=drops, killcount=killcount, team=team, playernames=autocomplete.player_names(), partial_completions=round(partial_completions, 2), relevant_drops=relevant_drops)




@user_routes.route('/leaderboard', methods=['GET'])
def leaderboard():
    if not board.is_board_globally_visible(current_user):
        return board.hidden_board()

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

    teams_gp_earned = defaultdict(int)

    players = []
    for player in database.get_players():
        player = db_entities.Player(player)
        players.append(player)

        total_gold += player.gp_gained
        total_deaths += player.deaths
        total_pets += player.pet_count
        total_tiles += player.tiles_completed

        teams_gp_earned[player.team_id] = teams_gp_earned[player.team_id] + player.gp_gained

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


    total_tiles = round(total_tiles, 2)
    players = sorted(players, key=lambda player: (player.tiles_completed, player.gp_gained), reverse=True)

    for player in players:
        player.gp_gained = scapify.int_to_gp(player.gp_gained)
        player.tiles_completed = round(player.tiles_completed, 2)


    teams = []
    for team in database.get_teams():
        teams.append(db_entities.Team(team))

    teams = sorted(teams, key=lambda team: (team.team_points, teams_gp_earned[team.team_id]), reverse=True)

    team_partial_tiles = defaultdict(int)
    player_partials = defaultdict(int)
    partial_tiles = 0
    for team in teams:
        for partial_tile in database.get_partial_completions_by_team_id(team.team_id):
            partial_tile = db_entities.PartialCompletion(partial_tile)
            team_partial_tiles[team.team_id] = team_partial_tiles[team.team_id] + partial_tile.partial_completion
            partial_tiles = partial_tiles + partial_tile.partial_completion
            player_partials[partial_tile.player_id] = player_partials[
                                                                partial_tile.player_id] + partial_tile.partial_completion
    partial_tiles = round(partial_tiles, 2)
    for key, value in team_partial_tiles.items():
        team_partial_tiles[key] = round(value, 2)
    for key, value in player_partials.items():
        player_partials[key] = round(value, 2)

    if most_tiles_player is not None:
        most_tiles_player.tiles_completed = round(most_tiles_player.tiles_completed, 2)
    partial_tiles = round(partial_tiles, 2)

    return render_template('user_templates/leaderboard.html', teams=teams, players=players, most_tiles_player=most_tiles_player,
                           most_gold_player=most_gold_player, most_pets_player=most_pets_player,
                           most_deaths_player=most_deaths_player,
                           total_pets=total_pets, total_tiles=total_tiles, total_gold=scapify.int_to_gp(total_gold),
                           total_deaths=total_deaths, partial_tiles=partial_tiles, team_partial_tiles=team_partial_tiles, player_partials=player_partials, teams_gp_earned=teams_gp_earned)
