def spoof_pet(player_name, pet_name):
    request = {
        "content": "%USERNAME% has a funny feeling they are being followed",
        "playerName": player_name,
        "extra": {
            "petName": pet_name,
            "milestone": "5,000 killcount",
            "duplicate": "false"
        },
        "type": "PET"
    }
    return request
