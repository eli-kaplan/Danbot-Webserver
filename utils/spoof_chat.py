# Example usage in a test
def spoof_chat(player_name, chat_message):
    request = {

                'type': 'CHAT',
                'playerName': player_name,
                'discordUser': {'id': '5'},
                "extra": {
                    "type": "GAMEMESSAGE",
                    "message": chat_message
                }
    }
    return request
