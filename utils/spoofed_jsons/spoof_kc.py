

# Example usage in a test
def kc_spoof_json(player_name, boss_name, quantity=1):
    request = {

                'type': 'KILL_COUNT',
                'playerName': player_name,
                'extra':
                    {
                        'boss': boss_name,
                        'quantity': quantity
                    },
                'discordUser': {'id': '202973806749286400'},

    }
    return request
