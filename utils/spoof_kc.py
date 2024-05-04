

# Example usage in a test
def kc_spoof_json(player_name, boss_name):
    request = {

                'type': 'KILL_COUNT',
                'playerName': player_name,
                'extra':
                    {
                        'boss': boss_name
                    },
                'discordUser': {'id': '202973806749286400'},

    }
    return request
