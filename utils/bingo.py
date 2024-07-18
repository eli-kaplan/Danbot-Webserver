from utils import database, db_entities
from utils.db_entities import Drop


class TileProgress:
    def __init__(self):
        self.team = None
        self.tile = None
        self.status_text = "Something went wrong in calculating your progress. Please contact Danbis"
        self.progress_value = 0
        self.completions = 0



def get_drop_progress(tile_progress):
    tile_completion_count = tile_progress.completions
    tile = tile_progress.tile
    team = tile_progress.team
    triggers = tile.tile_triggers
    and_triggers = triggers.split(',')
    trigger_value = database.get_manual_progress_by_tile_id_and_team_id(tile.tile_id, team.team_id)
    for i in range(0, len(and_triggers)):
        trigger = and_triggers[i].strip()
        drops = []
        for or_trigger in trigger.split('/'):
            or_trigger = or_trigger.strip()
            for drop in database.get_drops_by_item_name_and_team_id(or_trigger, team.team_id):
                drops.append(drop)

        if tile.tile_unique_drops == "True":
            if len(drops) > tile_completion_count:
                trigger_value = trigger_value + int(tile.tile_trigger_weights[i])
            continue
        else:
            for drop in drops:
                drop = Drop(drop)
                trigger_value = int(tile.tile_trigger_weights[i]) * int(drop.drop_quantity) + trigger_value

    tile_progress.status_text = f"You have {trigger_value % tile.tile_triggers_required} / {tile.tile_triggers_required} of the drops required to complete this tile\n"
    if len(drops) > 0:
        tile_progress.status_text += "Your current drops are:\n"
    for drop in drops:
        tile_progress.status_text = tile_progress.status_text + drop.drop_quantity + " x " + drop.drop_name + "\n"
    return tile_progress


def get_set_progress(tile_progress):
    return tile_progress


def get_killcount_progress(tile_progress):
    return tile_progress


def get_niche_progress(tile_progress):
    return tile_progress


def get_chat_progress(tile_progress):
    return tile_progress


def get_progress(team_id, tile_id):
    tile_progress = TileProgress()

    team = database.get_team_by_id(team_id)
    if team is not None:
        tile_progress.team = db_entities.Team(team)

    tile = database.get_tile_by_id(tile_id)
    if tile is not None:
        tile_progress.tile = db_entities.Tile(tile)

    # Get the tile completions
    tile_progress.completions = len(database.get_completed_tiles_by_team_id_and_tile_id(tile_progress.team.team_id, tile_progress.tile.tile_id))

    # If the tile has been completed more or equal to max allowed, return tile progress stating as such
    if tile_progress.completions >= tile_progress.tile.tile_repetition:
        tile_progress.status_text = f"This tile is fully complete. You have {tile_progress.completions}/{tile_progress.tile.tile_repetition} completed."
        tile_progress.progress_value = 1
        return tile_progress

    if tile_progress.tile.tile_type == "DROP":
        return get_drop_progress(tile_progress)
    if tile_progress.tile.tile_type == "SET":
        return get_set_progress(tile_progress)
    if tile_progress.tile.tile_type == "KILLCOUNT":
        return get_killcount_progress(tile_progress)
    if tile_progress.tile.tile_type == "NICHE":
        return get_niche_progress(tile_progress)
    if tile_progress.tile.tile_type == "CHAT":
        return get_chat_progress(tile_progress)


# def check_progress(tile, team):
#     tile_completion_count = len(database.get_completed_tiles_by_team_id_and_tile_id(team.team_id, tile.tile_id))
#
#     if tile.tile_type == "DROP":
#         # Check if the tile was completed or if it was just progressing the tile
#         triggers = tile.tile_triggers
#         and_triggers = triggers.split(',')
#         trigger_value = int(database.get_manual_progress_by_tile_id_and_team_id(tile.tile_id, team.team_id))
#         drops_found = []
#         for i in range(0, len(and_triggers)):
#             # Check the current trigger adding up any or triggers into a cumulative variable list called "drops"
#             trigger = and_triggers[i].strip()
#             drops = []
#             for or_trigger in trigger.split('/'):
#                 or_trigger = or_trigger.strip()
#                 for drop in database.get_drops_by_item_name_and_team_id(or_trigger, team.team_id):
#                     drops.append(drop)
#
#             # If the tile is unique ignore quantity / duplicates
#             if tile.tile_unique_drops == "True":
#                 if len(drops) > tile_completion_count:
#                     trigger_value = trigger_value + int(tile.tile_trigger_weights[i])
#                     drops_found.append(or_trigger)
#                 continue
#             # else multiply the drop quantity for each drop by the trigger weight
#             else:
#                 for drop in drops:
#                     drop = Drop(drop)
#                     trigger_value = int(tile.tile_trigger_weights[i]) * int(drop.drop_quantity) + trigger_value
#         if trigger_value % tile.tile_triggers_required == 0:
#             return f"You have no progress on {tile.tile_name}"
#         result = f"{tile.tile_name} is {trigger_value % tile.tile_triggers_required} / {tile.tile_triggers_required} from being completed!\n"
#         if tile.tile_unique_drops == "True":
#             result = result + f"You have already found "
#             if len(drops_found) == 0:
#                 result = result + "- None"
#             else:
#                 for found in drops_found:
#                     result = result + "\n- " + found
#         if tile_completion_count > 0:
#             result = result + f"- You have completed this tile {tile_completion_count} times.\n"
#     if tile.tile_type == "SET":
#         # Each set is separated by a '/' character
#         result = ""
#         missing_items = []
#         for set in tile.tile_triggers.split('/'):
#             current_missing_set = []
#             for item in set.split(','):
#                 # Get the item name from the set and check if it exists in the db with the given team id
#                 item = item.strip()
#                 drops = database.get_drops_by_item_name_and_team_id(item, team.team_id)
#
#                 # If drops has a length of 0 nobody on the team has gotten this drop yet
#                 if len(drops) <= tile_completion_count:
#                     is_complete = False  # Flag the tile as incomplete
#                     current_missing_set.append(str(item))
#                     result = result + "-" + str(item) + "-"  # Add the missing item to the description
#             missing_items.append(current_missing_set)
#             # If is_complete is still true, every item from the set has been acquired and the tile is complete
#             result = f"For {tile.tile_name} you are missing:\n"
#             for sets in missing_items:
#                 result = result + "- "
#                 for item in sets:
#                     result = result + item + ", "
#                 result = result + "\n"
#     if tile.tile_type == "NICHE":
#         niche_progress = database.get_manual_progress_by_tile_name_and_team_name(tile.tile_name, team.team_name)
#         if tile_completion_count >= int(tile.tile_repetition):
#             result = f"You have fully completed {tile.tile_name}\n"
#         else:
#             result = f"You have completed {tile.tile_name} {tile_completion_count} times. You are {int(niche_progress % tile.tile_triggers_required)}/{tile.tile_triggers_required} from your next completion\n"
#     return result