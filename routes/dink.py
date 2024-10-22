import os
from collections import defaultdict

from flask import Blueprint, jsonify, request
import json

from utils import database, db_entities, config
from utils.db_entities import Player, Team, Tile, Drop
from utils.send_webhook import send_webhook

drop_submission_route = Blueprint("dink", __name__)


# function to parse death data
def parse_death(data) -> dict[str, list[str]]:
    rsn = data['playerName']
    # Check if killerName exists
    if 'killerName' not in data['extra']:
        print("DEATH: " + rsn)
    else:
        print("DEATH: " + rsn + " died to " + data['extra']['killerName'])
    database.add_death_by_playername(rsn)
    # print data prettyfied
    # print(json.dumps(data, indent = 2))
    return True


# function to parse collection data
def parse_collection(data) -> dict[str, list[str]]:
    rsn = data['playerName']
    itemName = data['extra']['itemName']
    print(f"COLLECTION - {rsn} got a new collection log {itemName}")
    return True


# function to parse level data
def parse_level(data) -> dict[str, list[str]]:
    rsn = data['playerName']
    levelledSkills = data['extra']['levelledSkills']
    print(f"LEVEL - {rsn} levelled up {levelledSkills}")
    return True


def parse_loot(data, img_file) -> dict[str, list[str]]:

    # Get rsn
    rsn = data['playerName']

    # Handle discord attachment
    player = database.get_player_by_name(rsn)
    if player is None:
        return False
    player = db_entities.Player(player)

    team = database.get_team_by_id(player.team_id)
    if team is None:
        return False
    team = db_entities.Team(team)

    source = data['extra']['source']
    # Get item source
    itemSource = data['extra']['source']

    # Get item list
    items = data['extra']['items']
    # Loop through items
    for item in items:
        # Get item name
        itemName = item['name']
        # Get item price
        itemPrice = item['priceEach']
        # Get item quantity
        itemQuantity = item['quantity']
        # Get item total
        item_each = item['priceEach']

        # Add the item to the database
        print(f"LOOT: {player.player_name} - {itemName} x {itemQuantity} ({itemQuantity * itemPrice})")
        drop_pk = database.add_drop(team.team_id, player.player_id, rsn, itemName, item_each, itemQuantity, itemSource)

        # If the item is relevant
        if database.get_drop_whitelist_by_item_name(itemName) is not None:
            # Find the tile and team associated with this player / drop
            tile = Tile(database.get_tile_by_drop(itemName))
            team = Team(database.get_team_by_id(team.team_id))
            description = ""
            tile_completion_count = len(database.get_completed_tiles_by_team_id_and_tile_id(team.team_id, tile.tile_id))
            color = 0

            # Drop tile logic
            if tile.tile_type == "DROP":
                # If the tile has been completed too many times do nothing
                if tile_completion_count >= tile.tile_repetition:
                    continue

                database.add_relevant_drop(team.team_id, player.player_id, tile.tile_id, tile.tile_name, itemName, player.player_name, drop_pk)
                # Find the weight of the trigger and add the proportion to the players tile completions
                for i in range(len(tile.tile_triggers.split(','))):
                    for trigger in tile.tile_triggers.split(',')[i].split('/'):
                        if itemName == trigger.strip():
                            database.add_player_partial_completions(player.player_id, team.team_id, tile.tile_id, (int(tile.tile_trigger_weights[i]) * int(itemQuantity)) / tile.tile_triggers_required)
                # Check if the tile was completed or if it was just progressing the tile
                triggers = tile.tile_triggers
                and_triggers = triggers.split(',')
                trigger_value = database.get_manual_progress_by_tile_id_and_team_id(tile.tile_id, team.team_id)
                for i in range(0, len(and_triggers)):
                    # Check the current trigger adding up any or triggers into a cumulative variable list called "drops"
                    trigger = and_triggers[i].strip()
                    drops = []
                    for or_trigger in trigger.split('/'):
                        or_trigger = or_trigger.strip()
                        for drop in database.get_drops_by_item_name_and_team_id(or_trigger, team.team_id):
                            drops.append(drop)

                    # If the tile is unique ignore quantity / duplicates
                    if tile.tile_unique_drops == "True":
                        if len(drops) > 0:
                            trigger_value = trigger_value + int(tile.tile_trigger_weights[i])
                        continue
                    # else multiply the drop quantity for each drop by the trigger weight
                    else:
                        for drop in drops:
                            drop = Drop(drop)
                            trigger_value = int(tile.tile_trigger_weights[i]) * int(drop.drop_quantity) + trigger_value

                # If the trigger value is greater than triggers required multiplied by tile completion count then the tile has been completed an additional time
                if trigger_value >= tile.tile_triggers_required * (tile_completion_count + 1):# or (tile.tile_unique_drops == "True" and trigger_value >= tile.tile_triggers_required):
                    description = f"{tile.tile_name} completed! Congratulations! Your team has been awarded {tile.tile_points} point(s)!"
                    database.add_completed_tile(tile.tile_id, team.team_id)
                    description = description + f"\nYou have completed this tile {tile_completion_count + 1} times."
                    color = 65280 # Green
                    database.add_team_points(team.team_id, tile.tile_points)
                    current_trigger_rewards = 0
                    # Award partial_completions as full tile completions
                    for partial_completion in database.get_partial_completions_by_team_id_and_tile_id(team.team_id,
                                                                                                      tile.tile_id):
                        partial_completion = db_entities.PartialCompletion(partial_completion)
                        database.remove_partial_completion(partial_completion.partial_completion_pk)
                        database.add_player_tile_completions(partial_completion.player_id,
                                                             min(partial_completion.partial_completion, 1 - current_trigger_rewards))
                        if round(partial_completion.partial_completion,2) > round(1 - current_trigger_rewards, 2) and tile_completion_count + 1 < tile.tile_repetition:
                            database.add_player_partial_completions(player.player_id, team.team_id, tile.tile_id, partial_completion.partial_completion - (1 - current_trigger_rewards))
                        else:
                            current_trigger_rewards += partial_completion.partial_completion
                # Otherwise this drop only progressed the tile and didn't complete it
                else:
                    description = f"{tile.tile_name} is {trigger_value % tile.tile_triggers_required} / {tile.tile_triggers_required} from being completed!"
                    if tile_completion_count > 0:
                        description = description + f"\nYou have completed this tile {tile_completion_count} times."
                    color = 16776960 # Yellow

            # Set logic
            elif tile.tile_type == "SET":
                # If the tile has been completed too many times do nothing
                if tile_completion_count >= tile.tile_repetition:
                    continue

                database.add_relevant_drop(team.team_id, player.player_id, tile.tile_id, tile.tile_name, itemName, player.player_name, drop_pk)
                color = 16776960 # Yellow by default
                description = "You are still missing\n" # Assume set is not completed
                missing_items = []


                # Each set is separated by a '/' character
                for set in tile.tile_triggers.split('/'):
                    # If the item belongs to the current set, add 1 / the set length to the players tile completions
                    if itemName.lower() in set.lower():
                        database.add_player_partial_completions(player.player_id, team.team_id, tile.tile_id, 1 / len(set.split(',')))

                    # If every item from the set is found in the db is_complete will remain True
                    # Iterate through every item in the set (separated by ',') and check if the players team has at least one in the db
                    is_complete = True
                    current_missing_set = []
                    for item in set.split(','):
                        # Get the item name from the set and check if it exists in the db with the given team id
                        item = item.strip()
                        drops = database.get_drops_by_item_name_and_team_id(item, team.team_id)

                        # If drops has a length of 0 nobody on the team has gotten this drop yet
                        if len(drops) <= tile_completion_count:
                            is_complete = False                                 # Flag the tile as incomplete
                            current_missing_set.append(str(item))
                            description = description + "-" + str(item) + "-"   # Add the missing item to the description
                    missing_items.append(current_missing_set)
                    # If is_complete is still true, every item from the set has been acquired and the tile is complete
                    if is_complete:
                        description = f"{tile.tile_name} is completed! {team.team_name} has been awarded {tile.tile_points}\n points!"
                        color = 65280 # Green
                        database.add_team_points(team.team_id, tile.tile_points)
                        database.add_completed_tile(tile.tile_id, team.team_id)
                        for partial_completion in database.get_partial_completions_by_team_id_and_tile_id(team.team_id,
                                                                                                          tile.tile_id):
                            partial_completion = db_entities.PartialCompletion(partial_completion)
                            database.remove_partial_completion(partial_completion.partial_completion_pk)
                            database.add_player_tile_completions(partial_completion.player_id,
                                                                 partial_completion.partial_completion)
                        break
                    else:
                        description = "You are still missing\n"
                        for sets in missing_items:
                            description = description + "- "
                            for item in sets:
                                description = description + item + ", "
                            description = description + "\n"
            # Green = 65280, Yellow = 16776960
            # Alert the team of either their progress or their tile completion
            send_webhook(team.team_webhook, title=f"{rsn} got a {itemName} from {source}!", description=description, color=color, image=img_file)

    # Return true to signify the drop has been properly processed with no error
    return True


# function to parse slayer data
def parse_slayer(data) -> dict[str, list[str]]:
    rsn = data['playerName']
    slayer_monster = data['extra']['monster']
    kc_required = data['extra']['killCount']

    print(f"SLAYER - {rsn} finished their {slayer_monster} task ({kc_required} kill(s))")
    # print data prettyfied
    # print(json.dumps(data, indent = 2))
    return False


# function to parse quest data
def parse_quest(data) -> dict[str, list[str]]:
    rsn = data['playerName']
    questName = data['extra']['questName']

    print(f"QUEST - {rsn} completed {questName}")

    return True


# function to parse clue data
def parse_clue(data):
    rsn = data['playerName']
    clueType = data['extra']['clueType']

    print(f"CLUE: {rsn} - {clueType}")
    return True


# function to parse kill count data
def parse_kill_count(data, img_file) -> dict[str, list[str]]:
    rsn = data['playerName']
    boss_name = data['extra']['boss']
    print(f"KILLCOUNT: {rsn} - {boss_name}")

    try:
        quantity = data['extra']['quantity']
    except:
        quantity = 1

    player = database.get_player_by_name(rsn)
    if player is None:
        return False
    player = db_entities.Player(player)
    player_id = player.player_id

    team = database.get_team_by_id(player.team_id)
    if team is None:
        return False
    team = db_entities.Team(team)
    team_id = team.team_id

    database.add_killcount(player_id, team_id, boss_name, quantity)
    if database.get_drop_whitelist_by_item_name(boss_name) is not None:
        tile = Tile(database.get_tile_by_drop(boss_name))
        team = Team(database.get_team_by_id(team_id))
        tile_completion_count = len(database.get_completed_tiles_by_team_id_and_tile_id(team_id, tile.tile_id))

        if tile_completion_count >= tile.tile_repetition:
            return True

        killcount_weights = defaultdict(int)
        for i in range(len(tile.tile_trigger_weights)):
            killcount_weights[tile.tile_triggers.split(',')[i].strip().lower()] = int(tile.tile_trigger_weights[i])

        database.add_player_partial_completions(player_id, team.team_id, tile.tile_id, (killcount_weights[boss_name.lower()] * quantity) / tile.tile_triggers_required)
        team_killcount = database.get_manual_progress_by_tile_id_and_team_id(tile.tile_id, team.team_id)
        total_killcount = []
        for boss_trigger in tile.tile_triggers.split(','):
            killcounts = database.get_killcount_by_team_id_and_boss_name(team.team_id, boss_trigger.strip())
            for killcount in killcounts:
                killcount = db_entities.Killcount(killcount)
                total_killcount.append(killcount)
                team_killcount = team_killcount + (killcount.kills * killcount_weights[killcount.boss_name.lower()])

        if team_killcount >= tile.tile_triggers_required * (tile_completion_count + 1):
            database.add_completed_tile(tile.tile_id, team_id)
            database.add_team_points(team_id, tile.tile_points)
            description = (f"You have completed {tile.tile_name}! You have {tile_completion_count + 1} total completions"
                           f" with the following killcount\n")
            for killcount in total_killcount:
                player_ = database.get_player_by_id(killcount.player_id)
                player_ = db_entities.Player(player_)
                description = description + f"- {player_.player_name} with {killcount.kills} {killcount.boss_name} kills\n"
            send_webhook(team.team_webhook, f"{tile.tile_name} completed!", description=description,
                         color=65280, image=img_file)
            # Todo update player tile completions based on partial tile completion table
            current_trigger_rewards = 0
            for partial_completion in database.get_partial_completions_by_team_id_and_tile_id(team.team_id,
                                                                                              tile.tile_id):
                partial_completion = db_entities.PartialCompletion(partial_completion)
                database.remove_partial_completion(partial_completion.partial_completion_pk)
                database.add_player_tile_completions(partial_completion.player_id,
                                                     min(partial_completion.partial_completion,
                                                         1 - current_trigger_rewards))
                if round(partial_completion.partial_completion, 2) > round(1 - current_trigger_rewards,
                                                                           2) and tile_completion_count + 1 < tile.tile_repetition:
                    database.add_player_partial_completions(player.player_id, team.team_id, tile.tile_id,
                                                            partial_completion.partial_completion - (1 - current_trigger_rewards))
                else:
                    current_trigger_rewards += partial_completion.partial_completion
        elif boss_name.lower() == "TzTok-Jad".lower() or boss_name.lower() == "TzTok-Zuk".lower() or boss_name.lower() == "Sol-Heredit".lower():
            send_webhook(team.team_webhook, f"{player.player_name} killed {boss_name}! You are {(team_killcount % tile.tile_triggers_required)}/{tile.tile_triggers_required} from completing {tile.tile_name}",
                         description="", color=16776960, image=img_file)
            drop_name = ""
            if boss_name.lower() == "TzTok-Jad".lower():
                drop_name = "Fire cape"
            if boss_name.lower() == "TzTok-Zuk".lower():
                drop_name = "Infernal cape"
            if boss_name.lower() == "Sol-Heredit".lower():
                drop_name = "Dizana's quiver"
            drop_pk = database.add_drop(team.team_id, player.player_id, player.player_name, drop_name, 0, 1, boss_name.lower())
            database.add_relevant_drop(team.team_id, player.player_id, tile.tile_id, tile.tile_name, boss_name, player.player_name, drop_pk)
    return True


# function to parse combat achievement data
def parse_combat_achievement(data) -> dict[str, list[str]]:
    # print data prettyfied
    # print(json.dumps(data, indent = 2))
    rsn = data['playerName']
    achievement = data['extra']['task']
    tier = data['extra']['tier']

    print("COMBAT_ACHIEVEMENT: " + rsn + " - " + achievement + " (" + tier + ")")
    return []


# function to parse pet data
def parse_pet(data, img_file) -> dict[str, list[str]]:
    screenshotItems: dict[str, list[str]] = {}
    # print data prettyfied
    rsn = data['playerName']
    pet = data['extra']['petName']
    print(f"PET: {rsn} - {pet}")

    PET_POINTS = 0.5
    black_listed_pets = []

    player = database.get_player_by_name(rsn)
    if player is not None:
        player = db_entities.Player(player)
    else:
        return False

    team = database.get_team_by_id(player.team_id)
    team = db_entities.Team(team)
    database.add_pet_by_playername(rsn)

    # If a pet tile exists change behavior based on tile input
    pet_tile = database.get_tile_by_type("PET")
    if len(pet_tile) > 0:
        pet_tile = db_entities.Tile(pet_tile[0])
        tile_completion_count = len(database.get_completed_tiles_by_team_id_and_tile_id(team.team_id, pet_tile.tile_id))
        if pet in [trigger.strip() for trigger in pet_tile.tile_triggers.split(',')] or (tile_completion_count >= pet_tile.tile_repetition and pet_tile.tile_repetition > 0):
            send_webhook(team.team_webhook, f"{player.player_name} is being followed by {pet}!", description="Too bad its not worth any points....", color=16776960, image=img_file)
        else:
            database.add_player_tile_completions(player.player_id, 1)
            database.add_team_points(team.team_id, pet_tile.tile_points)
            database.add_completed_tile(pet_tile.tile_id, team.team_id)
            send_webhook(team.team_webhook, f"{player.player_name} is being followed by {pet}!", description=f"{team.team_name} has been awarded {pet_tile.tile_points} points!", color=65280, image=img_file)

    # If no pet tile exists, default setup configured here
    else:
        if pet in black_listed_pets:
            send_webhook(team.team_webhook, f"{player.player_name} is being followed by {pet}!",
                         description="Too bad its not worth any points....", color=16776960, image=img_file)
        else:
            database.add_player_tile_completions(player.player_id, 1)
            database.add_team_points(team.team_id, PET_POINTS)
            send_webhook(team.team_webhook, f"{player.player_name} is being followed by {pet}!", description=f"{team.team_name} has been awarded {PET_POINTS} points!", color=65280, image=img_file)

    return True


# function to parse speedrun data
def parse_speedrun(data) -> dict[str, list[str]]:
    # print("SPEEDRUN")
    # print data prettyfied
    # print(json.dumps(data, indent = 2))
    return False


# function to parse barbarian assault gamble data
def parse_barbarian_assault_gamble(data) -> dict[str, list[str]]:
    # print("BARBARIAN_ASSAULT_GAMBLE")
    # print data prettyfied
    # print(json.dumps(data, indent = 2))
    return True


# function to parse player kill data
def parse_player_kill(data) -> dict[str, list[str]]:
    rsn = data['playerName']
    victim = data['extra']['victimName']
    print(f"PLAYER_KILL - {rsn} killed {victim}")
    # print data prettyfied
    # print(json.dumps(data, indent = 2))
    return True


# function to parse group storage data
def parse_group_storage(data) -> dict[str, list[str]]:
    # print("GROUP_STORAGE")
    # print data prettyfied
    # print(json.dumps(data, indent = 2))
    return True


# function to parse grand exchange data
def parse_grand_exchange(data) -> dict[str, list[str]]:
    # print("GRAND_EXCHANGE")
    # print data prettyfied
    # print(json.dumps(data, indent = 2))
    return True


# function to parse trade data
def parse_trade(data) -> dict[str, list[str]]:
    rsn = data['playerName']
    other_rsn = data['extra']['counterparty']

    print(f"TRADE - {rsn} and {other_rsn}")
    rsn_recieved_list = []
    for receivedItem in data['extra']['receivedItems']:
        rsn_recieved_list.append(f"{receivedItem['name']} x {receivedItem['quantity']},")
    print(f"{rsn} received: {rsn_recieved_list}")
    other_received_list = []
    for other_received in data['extra']['givenItems']:
        other_received_list.append(f"{other_received['name']} x {other_received['quantity']},")
    print(f"{other_rsn} received: {other_received_list}")

    return True

# function to delegate parsing to its own function basing on the 'type' data
def parse_chat(data, img_file):
    rsn = data['playerName']
    chat_text = data['extra']['message']
    print(f"CHAT: {rsn} - \"{chat_text}\"")

    tile = database.get_tile_by_drop(chat_text)
    if tile is None:
        return False
    tile = db_entities.Tile(tile)

    player = database.get_player_by_name(rsn)
    if player is None:
        return False
    player = db_entities.Player(player)

    team = database.get_team_by_id(player.team_id)
    if team is None:
        return False
    team = db_entities.Team(team)

    tile_completions = len(database.get_completed_tiles_by_team_id_and_tile_id(team.team_id, tile.tile_id))

    if tile_completions >= tile.tile_repetition:
        return False

    database.add_chats(player.player_id, team.team_id, tile.tile_id, chat_text)
    database.add_player_partial_completions(player.player_id, team.team_id, tile.tile_id, int(tile.tile_trigger_weights[0]) / tile.tile_triggers_required)

    total_chats = len(database.get_chats_by_team_id_and_tile_id(team.team_id, tile.tile_id))
    if total_chats >= tile.tile_triggers_required * (tile_completions + 1):
        database.add_completed_tile(tile.tile_id, team.team_id)
        database.add_team_points(team.team_id, tile.tile_points)
        send_webhook(team.team_webhook, title=f"{player.player_name} finished {tile.tile_name}!", description=f"", color=65280, image=img_file)
        for partial_completion in database.get_partial_completions_by_team_id_and_tile_id(team.team_id, tile.tile_id):
            partial_completion = db_entities.PartialCompletion(partial_completion)
            database.remove_partial_completion(partial_completion.partial_completion_pk)
            database.add_player_tile_completions(partial_completion.player_id, partial_completion.partial_completion)
            if chat_text == "You are victorious!":
                database.add_relevant_drop(team.team_id, player.player_id, tile.tile_id, tile.tile_name, "LMS Win", player.player_name)
    else:
        send_webhook(team.team_webhook, title=f"{tile.tile_name} progress!", description=f"Thanks to {player.player_name}, you are {total_chats % tile.tile_triggers_required}/{tile.tile_triggers_required} from completing this tile", color=16776960, image=img_file )

    return True

# function to parse leagues area data
def parse_leagues_area(data) -> dict[str, list[str]]:
    # print("LEAGUES_AREA")
    # print data prettyfied
    # print(json.dumps(data, indent = 2))
    return True


# function to parse leagues relic data
def parse_leagues_relic(data) -> dict[str, list[str]]:
    # print("LEAGUES_RELIC")
    # print data prettyfied
    # print(json.dumps(data, indent = 2))
    return True


# function to parse leagues task data
def parse_leagues_task(data) -> dict[str, list[str]]:
    # print("LEAGUES_TASK")
    # print data prettyfied
    # print(json.dumps(data, indent = 2))
    return True


# function to parse login data
def parse_login(data) -> dict[str, list[str]]:
    rsn = data['playerName']
    print(f"LOGIN - {rsn}")

    return True





def parse_json_data(json_data, img_file) -> dict[str, list[str]]:
    data = json.loads(json_data)

    # types are: 'DEATH', 'COLLECTION, 'LEVEL', 'LOOT', 'SLAYER', 'QUEST',
    # 'CLUE', 'KILL_COUNT', 'COMBAT_ACHIEVEMENT', 'PET', 'SPEEDRUN', 'BARBARIAN_ASSAULT_GAMBLE',
    # 'PLAYER_KILL', 'GROUP_STORAGE', 'GRAND_EXCHANGE', 'TRADE', 'LEAGUES_AREA', 'LEAGUES_RELIC',
    # 'LEAGUES_TASK', and 'LOGIN'

    if 'type' in data:
        type = data['type']
        if type == 'DEATH':
            return parse_death(data)
        elif type == 'COLLECTION':
            return parse_collection(data)
        elif type == 'LEVEL':
            return parse_level(data)
        elif type == 'LOOT':
            return parse_loot(data, img_file)
        elif type == 'SLAYER':
            return parse_slayer(data)
        elif type == 'QUEST':
            return parse_quest(data)
        elif type == 'CLUE':
            return parse_clue(data)
        elif type == 'KILL_COUNT':
            return parse_kill_count(data, img_file)
        elif type == 'COMBAT_ACHIEVEMENT':
            return parse_combat_achievement(data)
        elif type == 'PET':
            return parse_pet(data, img_file)
        elif type == 'SPEEDRUN':
            return parse_speedrun(data)
        elif type == 'BARBARIAN_ASSAULT_GAMBLE':
            return parse_barbarian_assault_gamble(data)
        elif type == 'PLAYER_KILL':
            return # parse_player_kill(data)
        elif type == 'GROUP_STORAGE':
            return parse_group_storage(data)
        elif type == 'GRAND_EXCHANGE':
            return parse_grand_exchange(data)
        elif type == 'TRADE':
            return parse_trade(data)
        elif type == 'CHAT':
            return parse_chat(data, img_file)
        elif type == 'LEAGUES_AREA':
            return parse_leagues_area(data)
        elif type == 'LEAGUES_RELIC':
            return parse_leagues_relic(data)
        elif type == 'LEAGUES_TASK':
            return parse_leagues_task(data)
        elif type == 'LOGIN':
            return parse_login(data)
        else:
            print(f"Unknown type: {type}")
    else:
        print(f"Unknown data: {data}")

    return []



@drop_submission_route.route('', methods=['POST'])
def handle_request():
    if not config.enable_tracking():
        return jsonify({"message": "Not currently tracking"})

    data = request.form
    try:
        img_file = request.files['file']
    except:
        img_file = None
    if 'payload_json' in data:
        json_data = data['payload_json']
        try:
            result = parse_json_data(json_data, img_file)
        except Exception as e:
            print("Error parsing JSON data: " + str(e))
            print(json.dumps(json_data, indent=2))
            return jsonify({"message": "Error parsing JSON data: " + str(e)})

    if result:
        return jsonify({"message": "Drop successfully submitted"})
    return jsonify({"message": "No action recorded"})