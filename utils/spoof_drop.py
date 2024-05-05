

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
                        'source': 'Admin',
                    },
                'discordUser': {'id': '202973806749286400'},

    }
    return request
