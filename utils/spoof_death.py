# Example usage in a test
def spoof_death(player_name):
    request = {

                'type': 'DEATH',
                'playerName': player_name,
                'discordUser': {'id': '5'},
                'extra': {

                }

    }
    return request
