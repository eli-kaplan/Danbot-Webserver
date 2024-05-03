import json

import pytest


def replace_values_in_request(request, player_name, item_name, item_quantity):
    # Replace player name
    request['playerName'] = player_name

    # Replace item name and quantity
    for item in request['extra']['items']:
        item['name'] = item_name
        item['quantity'] = item_quantity

    return request


# Example usage in a test
def item_spoof_json(player_name, item_name, item_quantity):
    request = {

                'type': 'LOOT',
                'playerName': player_name,
                'extra':
                    {
                        'items':
                            [
                                {'id': 526, 'quantity': item_quantity, 'priceEach': 113, 'name': item_name},
                            ],
                        'source': 'Guard',
                    },
                'discordUser': {'id': '202973806749286400'},

    }
    return request
